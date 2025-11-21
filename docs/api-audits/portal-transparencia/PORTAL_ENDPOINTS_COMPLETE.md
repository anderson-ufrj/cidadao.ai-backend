# Portal da Transparência - Endpoints Completos

Baseado em documentação oficial e testes práticos.

## Base URL
```
http://api.portaldatransparencia.gov.br/api-de-dados
```

## Autenticação
Header: `chave-api-dados: YOUR_API_KEY`

## Endpoints Disponíveis

### 1. SERVIDORES (Servidores Públicos)

#### GET /servidores
Lista servidores públicos
- **Parâmetros**:
  - `pagina` (int): Página (obrigatório)
  - `nome` (string): Filtro por nome (opcional)
  - `cpf` (string): Filtro por CPF (opcional)
  - `orgao` (string): Código do órgão (opcional)

#### GET /servidores/{cpf}
Dados de um servidor específico por CPF

#### GET /servidores/{cpf}/remuneracao
Remuneração de um servidor por CPF
- **Parâmetros**:
  - `mesAno` (string): Mês/Ano no formato MM/YYYY

### 2. CONTRATOS

#### GET /contratos
Lista contratos
- **Parâmetros**:
  - `pagina` (int): Página (obrigatório)
  - `codigoOrgao` (string): Código do órgão (obrigatório)
  - `dataInicial` (string): Data inicial formato DD/MM/YYYY (opcional)
  - `dataFinal` (string): Data final formato DD/MM/YYYY (opcional)

### 3. DESPESAS

#### GET /despesas/documentos
Despesas por documento
- **Parâmetros**:
  - `codigoOrgao` (string): Código do órgão (obrigatório)
  - `ano` (int): Ano (obrigatório)
  - `pagina` (int): Página (obrigatório)

#### GET /despesas/por-orgao
Despesas agrupadas por órgão
- **Parâmetros**:
  - `ano` (int): Ano (obrigatório)
  - `mes` (int): Mês (obrigatório)
  - `pagina` (int): Página (obrigatório)

### 4. FORNECEDORES

#### GET /fornecedores
Lista fornecedores
- **Parâmetros**:
  - `pagina` (int): Página (obrigatório)
  - `cpfCnpj` (string): CPF/CNPJ (opcional)

### 5. CONVÊNIOS

#### GET /convenios
Lista convênios
- **Parâmetros**:
  - `pagina` (int): Página (obrigatório)
  - `uf` (string): Sigla UF (opcional)
  - `municipio` (string): Código município (opcional)

### 6. LICITAÇÕES

#### GET /licitacoes
Lista licitações
- **Parâmetros**:
  - `codigoOrgao` (string): Código do órgão (obrigatório)
  - `pagina` (int): Página (obrigatório)

### 7. CARTÕES DE PAGAMENTO

#### GET /cartoes
Gastos com cartões corporativos
- **Parâmetros**:
  - `mesAno` (string): Mês/Ano MM/YYYY (obrigatório)
  - `pagina` (int): Página (obrigatório)
  - `cpf` (string): CPF portador (opcional)

### 8. VIAGENS

#### GET /viagens
Viagens a serviço
- **Parâmetros**:
  - `cpf` (string): CPF do viajante (opcional)
  - `dataIdaDe` (string): Data de início DD/MM/YYYY (opcional)
  - `dataIdaAte` (string): Data de fim DD/MM/YYYY (opcional)
  - `pagina` (int): Página (obrigatório)

### 9. EMENDAS PARLAMENTARES

#### GET /emendas
Emendas parlamentares
- **Parâmetros**:
  - `ano` (int): Ano (obrigatório)
  - `pagina` (int): Página (obrigatório)
  - `autor` (string): Nome do autor (opcional)

### 10. AUXÍLIO EMERGENCIAL

#### GET /auxilio-emergencial
Beneficiários do auxílio emergencial
- **Parâmetros**:
  - `mesAno` (string): Mês/Ano MM/YYYY (obrigatório)
  - `pagina` (int): Página (obrigatório)
  - `cpf` (string): CPF (opcional)

### 11. BOLSA FAMÍLIA

#### GET /bolsa-familia-por-municipio
Bolsa Família por município
- **Parâmetros**:
  - `mesAno` (string): Mês/Ano MM/YYYY (obrigatório)
  - `codigoIbge` (string): Código IBGE município (obrigatório)
  - `pagina` (int): Página (obrigatório)

### 12. BPC (Benefício de Prestação Continuada)

#### GET /bpc-por-municipio
BPC por município
- **Parâmetros**:
  - `mesAno` (string): Mês/Ano MM/YYYY (obrigatório)
  - `codigoIbge` (string): Código IBGE município (obrigatório)
  - `pagina` (int): Página (obrigatório)

### 13. CEIS (Empresas Inidôneas)

#### GET /ceis
Cadastro de Empresas Inidôneas e Suspensas
- **Parâmetros**:
  - `pagina` (int): Página (obrigatório)
  - `cnpj` (string): CNPJ (opcional)

### 14. CNEP (Empresas Punidas)

#### GET /cnep
Cadastro Nacional de Empresas Punidas
- **Parâmetros**:
  - `pagina` (int): Página (obrigatório)
  - `cnpj` (string): CNPJ (opcional)

### 15. SEGURO DEFESO

#### GET /seguro-defeso
Seguro defeso de pescadores
- **Parâmetros**:
  - `mesAno` (string): Mês/Ano MM/YYYY (obrigatório)
  - `pagina` (int): Página (obrigatório)

## Padrões Comuns

### Paginação
- Parâmetro `pagina` (começa em 1)
- Parâmetro `tamanhoPagina` (opcional, padrão 15, máximo 500)

### Formato de Datas
- Datas individuais: `DD/MM/YYYY`
- Mês/Ano: `MM/YYYY`

### Rate Limit
- 90 requisições por minuto

### Códigos de Órgão Comuns
- `20101` - Presidência da República
- `36000` - Ministério da Saúde
- `26000` - Ministério da Educação
- `54000` - Ministério da Economia

## Exemplo de Uso (Python)

```python
import httpx

async def buscar_servidor(nome: str, api_key: str):
    url = "http://api.portaldatransparencia.gov.br/api-de-dados/servidores"
    headers = {"chave-api-dados": api_key}
    params = {"nome": nome, "pagina": 1}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        return response.json()
```

## Limitações Conhecidas
- ~78% dos endpoints retornam 403 Forbidden (limitação da API)
- Alguns endpoints requerem parâmetros específicos não documentados
- Rate limit rigoroso (90 req/min)
- Dados atualizados mensalmente
