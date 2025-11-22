# Modelo de Solicitação de Acesso à API TCE-MG

**Data**: 2025-11-14
**Autor**: Anderson Henrique da Silva
**Projeto**: Cidadão.AI

---

## 📧 Email/Ofício para TCE-MG

### Assunto
Solicitação de Acesso à API de Dados Abertos do TCE-MG - Projeto Cidadão.AI

---

### Corpo da Mensagem

**Para: Tribunal de Contas do Estado de Minas Gerais**
**Departamento: Tecnologia da Informação / Dados Abertos**

Prezados(as) Senhores(as),

Meu nome é **Anderson Henrique da Silva**, natural de Minas Gerais, e estou desenvolvendo o **Cidadão.AI**, uma plataforma de análise e transparência governamental com foco em dados públicos brasileiros.

Venho por meio desta solicitar **acesso programático à API de Dados Abertos do TCE-MG** (`https://dadosabertos.tce.mg.gov.br`) para integração ao nosso sistema.

---

### 📋 Sobre o Projeto Cidadão.AI

**Descrição**: Plataforma de análise automatizada de dados de transparência governamental utilizando inteligência artificial multi-agente.

**Objetivo**: Facilitar o acesso e análise de dados públicos pelos cidadãos brasileiros, promovendo transparência e participação social.

**Tecnologia**: Sistema baseado em FastAPI com 17 agentes especializados para análise de contratos, licitações, despesas e indicadores fiscais.

**Cobertura Atual**:
- 20 APIs governamentais integradas (federais e estaduais)
- SICONFI (Tesouro Nacional) - 5.570 municípios
- TCE-SP (São Paulo) - 644 municípios
- TCE-CE (Ceará) - 185 municípios
- 12 portais CKAN estaduais

**Repositório**: GitHub público (código aberto em desenvolvimento)

---

### 🔍 Problemas Identificados

Realizamos testes técnicos detalhados no portal de dados abertos do TCE-MG e identificamos os seguintes impedimentos técnicos para integração:

#### 1. **Certificado SSL Não Verificável** ❌

**⚠️ IMPORTANTE**: O site está **FUNCIONANDO PERFEITAMENTE**. O problema é **APENAS O CERTIFICADO SSL**.

**Problema**: O certificado SSL de `dadosabertos.tce.mg.gov.br` não pode ser verificado por autoridades certificadoras reconhecidas.

**Erro Técnico**:
```
[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed:
unable to get local issuer certificate
```

**Evidência de que o site funciona**:
```
✅ COM SSL DESABILITADO (verify=False):
   Status: 200 OK
   Tamanho: 69.535 bytes
   Tipo: text/html
   → SITE FUNCIONA PERFEITAMENTE!

❌ COM SSL HABILITADO (verify=True - produção):
   Erro: [SSL: CERTIFICATE_VERIFY_FAILED]
   → APENAS O CERTIFICADO ESTÁ INVÁLIDO
```

**Impacto**:
- ✅ Portal está online e operacional
- ❌ Certificado SSL inválido impede uso seguro
- ❌ Impossibilita uso em ambiente de produção
- ❌ Requer desabilitar verificação SSL (inseguro)
- ❌ Expõe sistema a ataques man-in-the-middle
- ❌ Viola requisitos de segurança da informação

**Conclusão**: **O problema é simples e resolvível** - basta instalar um certificado SSL válido!

#### 2. **Endpoints de API Não Encontrados** ❌

**Problema**: Todos os endpoints CKAN padrão retornam 404 Not Found.

**Endpoints Testados**:
```
https://dadosabertos.tce.mg.gov.br/api                     → 404
https://dadosabertos.tce.mg.gov.br/api/3                   → 404
https://dadosabertos.tce.mg.gov.br/api/3/action            → 404
https://dadosabertos.tce.mg.gov.br/api/3/action/package_list → 404
https://dadosabertos.tce.mg.gov.br/api/datasets            → 404
https://dadosabertos.tce.mg.gov.br/api/municipios          → 404
https://dadosabertos.tce.mg.gov.br/api/contratos           → 404
```

**Resultado**: 0/8 endpoints funcionando

**Impacto**: Não conseguimos identificar como acessar os dados programaticamente.

#### 3. **Portal Estadual Restrito** ❌

**Portal Testado**: `https://dados.mg.gov.br/api/3`

**Problema**: Todos os endpoints retornam 403 Forbidden.

**Impacto**: Portal estadual requer autenticação ou cadastro prévio.

---

### 📊 Relatório de Testes

Anexamos relatório técnico completo com evidências dos testes realizados:
- Teste de certificado SSL (com e sem verificação)
- Descoberta de endpoints de API
- Teste de portal CKAN estadual
- Teste do cliente atual implementado
- Resultados detalhados com códigos de status HTTP

**Arquivo**: `test_tce_mg_detailed.py` (script de testes reproduzível)

---

### 🎯 Solicitações Específicas

Para viabilizar a integração do TCE-MG ao Cidadão.AI, solicitamos:

#### 1. **Correção do Certificado SSL** 🔒
- Instalação de certificado SSL válido emitido por CA reconhecida
- **OU** fornecimento do certificado CA do TCE-MG para instalação em nosso sistema
- **OU** orientação sobre configuração necessária

#### 2. **Documentação da API** 📚
- URLs dos endpoints disponíveis
- Parâmetros aceitos e formatos de requisição
- Schemas de resposta (JSON/XML)
- Exemplos de uso para cada endpoint
- Limites de taxa (rate limits) se aplicável

#### 3. **Concessão de Acesso** 🔑
- **Opção A**: Acesso público sem autenticação (preferencial)
- **Opção B**: Processo de registro para obtenção de credenciais
- **Opção C**: API key ou token de acesso
- Contato técnico para suporte em caso de problemas

#### 4. **Datasets Desejados** 📂

Temos interesse especial nos seguintes conjuntos de dados:

- **Municípios**: Lista dos 853 municípios de Minas Gerais (códigos IBGE)
- **Contratos**: Contratos públicos e aditivos contratuais
- **Licitações**: Processos licitatórios e modalidades
- **Despesas**: Execução orçamentária e empenhos
- **Receitas**: Arrecadação e receitas municipais/estaduais
- **Relatórios Fiscais**: RREO, RGF, demonstrativos contábeis
- **Fornecedores**: Cadastro de fornecedores e histórico

---

### ✅ Solução Temporária Atual

Enquanto aguardamos acesso à API do TCE-MG, estamos utilizando como **fallback** a API SICONFI do Tesouro Nacional, que fornece dados fiscais para todos os 853 municípios mineiros:

```
API: https://apidatalake.tesouro.gov.br/ords/siconfi/tt/
Cobertura: 5.570 municípios brasileiros (incluindo todos de MG)
Dados: RREO, RGF, DCA, entidades governamentais
Status: ✅ Funcionando perfeitamente
```

**Limitação**: Dados do SICONFI são mais genéricos (nível federal). Dados do TCE-MG seriam mais específicos e detalhados para análises estaduais/municipais.

---

### 🏠 Motivação Pessoal

Como mineiro, tenho especial interesse em disponibilizar análises detalhadas sobre a gestão pública do meu estado natal. Minas Gerais, com seus 853 municípios, representa uma parte significativa do Brasil, e ter acesso aos dados do TCE-MG enriqueceria enormemente nossa plataforma.

Acreditamos que ferramentas de transparência como o Cidadão.AI fortalecem a democracia e o controle social sobre a gestão pública.

---

### 📞 Informações de Contato

**Nome**: Anderson Henrique da Silva
**Email**: [seu-email]
**Projeto**: Cidadão.AI
**GitHub**: [link-repositório]
**Localização**: Minas Gerais, Brasil

**Disponibilidade**: Estou disponível para reuniões técnicas, apresentações do projeto ou esclarecimentos adicionais que se fizerem necessários.

---

### 📎 Anexos

1. **test_tce_mg_detailed.py** - Script de testes técnicos
2. **TCE_MG_INVESTIGATION_2025_11_14.md** - Relatório completo de investigação
3. **Screenshots** - Prints dos erros SSL e 404

---

### 🙏 Agradecimentos

Agradecemos antecipadamente pela atenção e esperamos contar com o apoio do TCE-MG na promoção da transparência e do acesso à informação pública.

Ficamos no aguardo de retorno sobre as possibilidades de acesso à API.

---

Atenciosamente,

**Anderson Henrique da Silva**
Desenvolvedor - Projeto Cidadão.AI
Minas Gerais, Brasil

---

## 📋 Checklist para Envio

Antes de enviar a solicitação, certifique-se de:

- [ ] Anexar relatório de testes (`test_tce_mg_detailed.py`)
- [ ] Anexar documentação técnica (`TCE_MG_INVESTIGATION_2025_11_14.md`)
- [ ] Tirar prints dos erros SSL
- [ ] Tirar prints dos erros 404
- [ ] Incluir informações de contato atualizadas
- [ ] Incluir link do repositório GitHub (se público)
- [ ] Revisar texto para linguagem formal
- [ ] Verificar se todos os anexos estão incluídos

---

## 🔍 Onde Enviar

**Opções de Contato TCE-MG**:

1. **Portal de Transparência**:
   - Site: https://www.tce.mg.gov.br
   - Seção: Fale Conosco / Ouvidoria

2. **E-SIC (Sistema de Informações ao Cidadão)**:
   - Plataforma oficial para solicitações de acesso à informação
   - Lei de Acesso à Informação (LAI)

3. **Departamento de TI**:
   - Buscar contato específico do setor de Tecnologia
   - Área de Dados Abertos / Transparência

4. **Redes Sociais**:
   - Twitter/X do TCE-MG (para divulgação)
   - LinkedIn (para contato profissional)

---

## ⏱️ Prazo Esperado

Conforme Lei de Acesso à Informação (LAI - Lei 12.527/2011):
- **Prazo padrão**: 20 dias
- **Prorrogação**: Mais 10 dias (se necessário)
- **Total máximo**: 30 dias

---

## 🎯 Resultados Esperados

**Melhor Cenário**:
- ✅ SSL corrigido
- ✅ Documentação de API fornecida
- ✅ Acesso público concedido
- ✅ Integração completada em 1 semana

**Cenário Realista**:
- ⚠️ SSL corrigido em 2-4 semanas
- ⚠️ API key fornecida após cadastro
- ⚠️ Documentação parcial disponível
- ✅ Integração completada em 1 mês

**Cenário Pessimista**:
- ❌ SSL não corrigido
- ❌ API não disponível publicamente
- ⚠️ Apenas acesso via downloads (CSV/Excel)
- ⚠️ Continuar usando SICONFI como fonte principal

---

**Documento Criado**: 2025-11-14
**Última Atualização**: 2025-11-14
**Status**: Pronto para envio
