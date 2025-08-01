---
title: "Autenticação"
sidebar_position: 2
description: "Guia abrangente de autenticação, autorização e segurança da API"
---

# Autenticação

## Visão Geral

A API do Cidadão.AI implementa um **sistema de autenticação multi-camadas** baseado em padrões da indústria, fornecendo controle de acesso seguro através de tokens JWT, integração OAuth 2.0 e permissões baseadas em funções.

## Métodos de Autenticação

### 1. Autenticação JWT (Principal)

A API usa **JSON Web Tokens (JWT)** como mecanismo de autenticação principal, seguindo as especificações RFC 7519.

#### Estrutura do Token

```json
{
  "header": {
    "alg": "RS256",
    "typ": "JWT",
    "kid": "2024-01-key"
  },
  "payload": {
    "sub": "550e8400-e29b-41d4-a716-446655440000",
    "email": "usuario@exemplo.com",
    "role": "usuario",
    "permissoes": ["ler:investigacoes", "escrever:relatorios"],
    "iat": 1706616000,
    "exp": 1706616900,
    "jti": "id-token-unico"
  },
  "signature": "..."
}
```

#### Ciclo de Vida do Token

```mermaid
graph LR
    Login[Login] --> Access[Token de Acesso<br/>15 minutos]
    Login --> Refresh[Token de Renovação<br/>7 dias]
    Access --> API[Requisições API]
    Access -.->|Expira| Renovar[Renovação de Token]
    Refresh --> Renovar
    Renovar --> Access
```

### 2. Integração OAuth 2.0

Suporte para provedores de autenticação de terceiros:

- **Google** (OpenID Connect)
- **GitHub** (OAuth 2.0)
- **Microsoft** (Azure AD)
- **Provedores SAML/OIDC personalizados**

#### Fluxo OAuth

```mermaid
sequenceDiagram
    participant Usuario
    participant App
    participant API
    participant OAuth
    
    Usuario->>App: Clique "Entrar com Google"
    App->>API: GET /auth/oauth/google/authorize
    API-->>App: URL de autorização
    App->>OAuth: Redirecionar para Google
    Usuario->>OAuth: Aprovar permissões
    OAuth->>App: Redirecionar com código
    App->>API: GET /auth/oauth/google/callback?code=...
    API->>OAuth: Trocar código por token
    OAuth-->>API: Informações do usuário
    API-->>App: Tokens JWT
```

### 3. Autenticação por Chave de API (Legado)

Para compatibilidade regressiva e comunicação serviço-a-serviço:

```http
X-API-Key: sk_live_50e8400-e29b-41d4-a716-446655440000
```

## Endpoints de Autenticação

### Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "usuario@exemplo.com",
  "senha": "senha-segura"
}
```

**Resposta:**
```json
{
  "token_acesso": "eyJhbGciOiJSUzI1NiIs...",
  "token_renovacao": "eyJhbGciOiJSUzI1NiIs...",
  "tipo_token": "Bearer",
  "expira_em": 900,
  "usuario": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "usuario@exemplo.com",
    "funcao": "usuario",
    "permissoes": ["ler:investigacoes", "escrever:relatorios"]
  }
}
```

### Renovação de Token

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "token_renovacao": "eyJhbGciOiJSUzI1NiIs..."
}
```

### Registro de Usuário

```http
POST /api/v1/auth/register
Authorization: Bearer {token_admin}
Content-Type: application/json

{
  "email": "novousuario@exemplo.com",
  "senha": "senha-segura",
  "funcao": "analista"
}
```

### Alterar Senha

```http
POST /api/v1/auth/change-password
Authorization: Bearer {token}
Content-Type: application/json

{
  "senha_atual": "senha-antiga",
  "nova_senha": "nova-senha-segura"
}
```

## Autorização

### Controle de Acesso Baseado em Funções (RBAC)

| Função | Descrição | Permissões |
|--------|-----------|------------|
| `admin` | Administrador do sistema | Acesso total a todos os recursos |
| `analista` | Analista de dados | Criar investigações, análises, relatórios |
| `visualizador` | Usuário somente leitura | Ver investigações e relatórios públicos |
| `servico` | Conta de serviço | Acesso à API para integrações |

### Modelo de Permissões

```python
class Permissao(Enum):
    # Investigações
    LER_INVESTIGACOES = "ler:investigacoes"
    ESCREVER_INVESTIGACOES = "escrever:investigacoes"
    DELETAR_INVESTIGACOES = "deletar:investigacoes"
    
    # Análises
    LER_ANALISES = "ler:analises"
    ESCREVER_ANALISES = "escrever:analises"
    
    # Relatórios
    LER_RELATORIOS = "ler:relatorios"
    ESCREVER_RELATORIOS = "escrever:relatorios"
    
    # Admin
    GERENCIAR_USUARIOS = "gerenciar:usuarios"
    VER_LOGS_AUDITORIA = "ver:auditoria"
    CONFIGURAR_SISTEMA = "configurar:sistema"
```

### Permissões de Nível de Recurso

```python
# Verificar propriedade
if investigacao.usuario_id != usuario_atual.id and not usuario_atual.eh_admin:
    raise ErroProibido("Você não tem permissão para acessar este recurso")

# Verificar acesso da equipe
if investigacao.id_equipe not in usuario_atual.ids_equipe:
    raise ErroProibido("Este recurso pertence a outra equipe")
```

## Headers de Segurança

### Headers de Requisição

```http
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
X-Client-Version: 1.0.0
```

### Headers de Resposta

```http
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
```

## Gerenciamento de Tokens

### Armazenamento de Tokens (Lado do Cliente)

```javascript
// Recomendações de armazenamento seguro
class GerenciadorToken {
  // Armazenar na memória para apps web
  private tokenAcesso: string;
  
  // Armazenar em armazenamento seguro para mobile
  async armazenarTokenRenovacao(token: string) {
    await SecureStore.setItemAsync('token_renovacao', token);
  }
  
  // Nunca armazenar em localStorage para apps sensíveis
  // Use cookies httpOnly quando possível
}
```

### Validação de Token

```python
def validar_token(token: str) -> PayloadToken:
    try:
        # Verificar assinatura
        payload = jwt.decode(
            token,
            CHAVE_PUBLICA,
            algorithms=["RS256"],
            options={"verify_exp": True}
        )
        
        # Verificar claims adicionais
        if payload.get("iss") != "https://api.cidadao.ai":
            raise ErroTokenInvalido("Emissor inválido")
            
        # Verificar se token não foi revogado
        if token_revogado(payload["jti"]):
            raise ErroTokenInvalido("Token foi revogado")
            
        return PayloadToken(**payload)
        
    except jwt.ExpiredSignatureError:
        raise ErroTokenExpirado("Token expirou")
    except jwt.InvalidTokenError as e:
        raise ErroTokenInvalido(f"Token inválido: {str(e)}")
```

## Autenticação Multi-Fator (MFA)

### Configuração TOTP

```http
POST /api/v1/auth/mfa/setup
Authorization: Bearer {token}

Resposta:
{
  "segredo": "JBSWY3DPEHPK3PXP",
  "codigo_qr": "data:image/png;base64,...",
  "codigos_backup": [
    "12345678",
    "87654321",
    ...
  ]
}
```

### Verificação MFA

```http
POST /api/v1/auth/mfa/verify
Content-Type: application/json

{
  "email": "usuario@exemplo.com",
  "senha": "senha",
  "codigo_totp": "123456"
}
```

## Gerenciamento de Sessão

### Configuração de Sessão

```python
CONFIG_SESSAO = {
    "expiracao_token_acesso": timedelta(minutes=15),
    "expiracao_token_renovacao": timedelta(days=7),
    "max_renovacoes": 5,
    "sessoes_concorrentes": 3,
    "timeout_inatividade": timedelta(hours=2)
}
```

### Monitoramento de Sessão Ativa

```http
GET /api/v1/auth/sessions
Authorization: Bearer {token}

Resposta:
{
  "sessoes": [
    {
      "id": "sessao-1",
      "dispositivo": "Chrome no Windows",
      "endereco_ip": "192.168.1.1",
      "localizacao": "São Paulo, BR",
      "ultima_atividade": "2025-01-30T10:15:30Z",
      "atual": true
    }
  ]
}
```

## Melhores Práticas de Segurança

### 1. Segurança de Tokens

```python
# Use geração randômica segura
def gerar_id_token():
    return secrets.token_urlsafe(32)

# Implemente rotação de tokens
def rotacionar_token_renovacao(token_antigo: str) -> tuple[str, str]:
    # Validar token antigo
    payload = validar_token(token_antigo)
    
    # Gerar novos tokens
    novo_acesso = criar_token_acesso(payload.sub)
    nova_renovacao = criar_token_renovacao(payload.sub)
    
    # Revogar token de renovação antigo
    revogar_token(token_antigo)
    
    return novo_acesso, nova_renovacao
```

### 2. Limitação de Taxa

```python
# Implementar atrasos progressivos para tentativas falhadas
TENTATIVAS_LOGIN = {
    1: 0,      # Sem atraso
    2: 1,      # 1 segundo
    3: 5,      # 5 segundos
    4: 15,     # 15 segundos
    5: 60,     # 1 minuto
    6: 300     # 5 minutos (bloqueio)
}
```

### 3. Log de Auditoria

```python
@log_auditoria(TipoEventoAuditoria.SUCESSO_AUTENTICACAO)
async def login(credenciais: RequisicaoLogin) -> RespostaLogin:
    # Lógica de autenticação
    pass

@log_auditoria(TipoEventoAuditoria.ACESSO_NAO_AUTORIZADO)
async def handle_unauthorized(request: Request):
    # Registrar tentativas não autorizadas
    pass
```

## Configuração OAuth

### Configuração de Provedores

```python
PROVEDORES_OAUTH = {
    "google": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "url_autorizacao": "https://accounts.google.com/o/oauth2/v2/auth",
        "url_token": "https://oauth2.googleapis.com/token",
        "escopo": ["openid", "email", "profile"]
    },
    "github": {
        "client_id": os.getenv("GITHUB_CLIENT_ID"),
        "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
        "url_autorizacao": "https://github.com/login/oauth/authorize",
        "url_token": "https://github.com/login/oauth/access_token",
        "escopo": ["user:email"]
    }
}
```

### Fluxo de Aprovação de Usuário

```mermaid
stateDiagram-v2
    [*] --> LoginOAuth
    LoginOAuth --> AprovacaoPendente
    AprovacaoPendente --> RevisaoAdmin
    RevisaoAdmin --> Aprovado: Admin aprova
    RevisaoAdmin --> Rejeitado: Admin rejeita
    Aprovado --> UsuarioAtivo
    Rejeitado --> [*]
```

## Tratamento de Erros

### Erros de Autenticação

| Código de Erro | Descrição | Status HTTP |
|----------------|-----------|-------------|
| `CREDENCIAIS_INVALIDAS` | Email/senha incorretos | 401 |
| `TOKEN_EXPIRADO` | Token de acesso expirou | 401 |
| `TOKEN_INVALIDO` | Token malformado ou adulterado | 401 |
| `PERMISSOES_INSUFICIENTES` | Falta permissões necessárias | 403 |
| `CONTA_BLOQUEADA` | Muitas tentativas falhadas | 423 |
| `MFA_OBRIGATORIO` | Deve fornecer código MFA | 428 |

### Exemplo de Resposta de Erro

```json
{
  "erro": {
    "codigo": "TOKEN_EXPIRADO",
    "mensagem": "Token de acesso expirou",
    "detalhes": {
      "expirou_em": "2025-01-30T10:15:30Z",
      "token_renovacao_valido": true
    },
    "id_requisicao": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

## Testando Autenticação

### Testes de Integração

```python
async def test_fluxo_autenticacao_completo():
    # 1. Registrar usuário
    resposta = await client.post("/auth/register", json={
        "email": "teste@exemplo.com",
        "senha": "senha-segura"
    })
    assert resposta.status_code == 201
    
    # 2. Login
    resposta = await client.post("/auth/login", json={
        "email": "teste@exemplo.com",
        "senha": "senha-segura"
    })
    tokens = resposta.json()
    
    # 3. Usar token de acesso
    resposta = await client.get(
        "/investigacoes",
        headers={"Authorization": f"Bearer {tokens['token_acesso']}"}
    )
    assert resposta.status_code == 200
    
    # 4. Renovar token
    resposta = await client.post("/auth/refresh", json={
        "token_renovacao": tokens["token_renovacao"]
    })
    assert "token_acesso" in resposta.json()
```

---

Próximo: [Referência de Endpoints →](./endpoints/index.md)