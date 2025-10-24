# 🇧🇷 Ecossistema Completo de APIs Governamentais Brasileiras

**Autor**: Anderson Henrique da Silva
**Data de Criação**: 2025-10-14
**Última Atualização**: 2025-10-14 16:00:00 -03:00
**Fonte**: Catálogo Conecta GOV.BR + Pesquisa Extensiva

---

## 📊 ESTATÍSTICAS GERAIS

| Categoria | Quantidade Identificada | Integradas | Pendentes |
|-----------|------------------------|------------|-----------|
| **APIs no Catálogo Oficial** | 32+ | 4 | 28+ |
| **APIs SERPRO** | 20+ | 1 | 19+ |
| **APIs Ministeriais** | 50+ | 8 | 42+ |
| **APIs Estaduais (TCEs)** | 27 | 6 | 21 |
| **APIs Municipais** | 100+ | 0 | 100+ |
| **TOTAL ESTIMADO** | **200+** | **17** | **183+** |

---

## 🏛️ PARTE 1: CATÁLOGO OFICIAL CONECTA GOV.BR

### ✅ Integradas (4)

1. **Portal da Transparência** ⚠️ PARCIAL
2. **IBGE Metadata** ✅ (via IBGE Client)
3. **Dados.gov.br** ✅
4. **SIOP/Orçamento** ⏸️ (não prioritário)

### 🚧 Pendentes no Catálogo (28+)

#### Identidade e Autenticação
5. **Acesso gov.br (Login Único)**
   - URL: https://www.gov.br/conecta/catalogo/apis/brasil-cidadao-login-unico
   - Função: SSO para serviços federais
   - Prioridade: 🔥 ALTA

#### Saúde
6. **CNS - Cartão Nacional de Saúde**
   - Função: Validação de usuários SUS
   - Prioridade: 🔥 ALTA

7. **RNDS - Rede Nacional de Dados em Saúde**
   - Função: Interoperabilidade de dados de saúde
   - Prioridade: 🔥 ALTA

8. **Registro de Ocupação Hospitalar COVID-19**
   - Prioridade: MÉDIA

9. **Notificações de Síndrome Gripal**
   - Prioridade: MÉDIA

#### Justiça e Segurança
10. **Certidão de Antecedentes Criminais**
    - URL: https://www.gov.br/conecta/catalogo/apis/certidao-de-antecedentes-criminais
    - Função: Consulta de antecedentes
    - Prioridade: 🔥 ALTA

#### Documentação e Registro
11. **Cadastro Base de Endereço (CEP)**
    - Função: Validação de CEP oficial
    - Prioridade: 🔥 ALTA

12. **Publicar no Diário Oficial da União - DOU**
    - Função: Acesso programático ao DOU
    - Prioridade: ALTA

#### Social
13. **Pessoa com Deficiência**
    - Função: Cadastro de PcD
    - Prioridade: ALTA

14. **Declaração de Aptidão ao Pronaf (DAP)**
    - Função: Agricultura familiar
    - Prioridade: MÉDIA

#### Ouvidoria e Participação
15. **Fala.Br - Ouvidorias**
    - Função: Sistema de ouvidorias
    - Prioridade: ALTA

16. **Acompanhamento de Serviço Público Digital**
    - Prioridade: MÉDIA

17. **Avaliação da Satisfação com Serviços Públicos Digitais**
    - Prioridade: MÉDIA

#### Orçamento e Finanças (SIOP)
18. **Acompanhamento da Execução das Empresas Estatais - SIOP**
19. **Alterações Orçamentárias SIOP**
20. **Consulta Execução Orçamentária SIOP**
21. **Emendas Individuais SIOP**
22. **Precatórios do SIOP**
23. **Qualitativo do SIOP**
24. **Quantitativo do SIOP**
25. **Receitas do SIOP**
26. **Avaliação do PPA**
27. **Monitoramento do PPA**

#### Pagamentos
28. **PagTesouro - Órgãos Arrecadadores**
29. **PagTesouro - Prestadores de Serviços de Pagamentos**

#### Integração Financeira
30. **Integra Siafi – Nota de Crédito e de Dotação**

#### Tributos
31. **Consulta Certidão Negativa de Débitos (CND)**
    - Função: Validação de regularidade fiscal
    - Prioridade: 🔥 ALTA

#### Servidores Públicos
32. **Registro de Referência - Servidores Públicos Federais (SIAPE Consultas)**
    - Função: Dados de servidores
    - Prioridade: ALTA

---

## 🏢 PARTE 2: APIs SERPRO (Serviço Federal de Processamento de Dados)

### 🔥 APIs Críticas Não Integradas

33. **Consulta CPF** 💰 PAGA
    - URL: https://www.serpro.gov.br/
    - Função: Validação completa de CPF direto da Receita Federal
    - Dados: Nome completo, nome social, data nascimento, situação cadastral, data inscrição
    - Volume: 120 milhões de consultas mensais (1869 clientes ativos)
    - Status: ⚠️ REQUER CONTRATO
    - **Alternativa GRATUITA**: Minha Receita (já integrado) ✅

34. **Consulta CNPJ Oficial** 💰 PAGA
    - URL: https://www.gov.br/conecta/catalogo/apis/consulta-cnpj
    - Função: Dados diretos da Receita Federal
    - Status: ⚠️ REQUER CONTRATO
    - **Alternativa GRATUITA**: Minha Receita (já integrado) ✅

35. **Consulta NFe (Nota Fiscal Eletrônica)** 💰 PAGA
    - Função: Validação de notas fiscais
    - Prioridade: 🔥 ALTA (para análise de fornecedores)
    - Status: ⚠️ REQUER CONTRATO

36. **Consulta RENAVAM** 💰 PAGA
    - Função: Dados veiculares
    - Prioridade: MÉDIA

37. **Consulta Receita Federal - Situação Fiscal** 💰 PAGA
    - Função: Regularidade tributária
    - Prioridade: ALTA

### Outras APIs SERPRO (15+)
38. Datavalid (validação biométrica)
39. Consulta Biometria Facial
40. Balcão Único
41. Consulta Débitos Trabalhistas
42. Consulta FGTS
43. Entre outras...

---

## 🏛️ PARTE 3: APIs POR MINISTÉRIO/ÓRGÃO

### Ministério da Fazenda / Receita Federal

44. **API Simples Nacional**
    - Função: Consulta enquadramento ME/EPP
    - Prioridade: ALTA
    - Status: 🔍 PESQUISAR

45. **API Notas Fiscais (SPED)**
    - Função: Sistema Público de Escrituração Digital
    - Prioridade: ALTA

46. **API Comércio Exterior (SISCOMEX)**
    - Função: Importação/exportação
    - Prioridade: MÉDIA

### Ministério do Trabalho e Emprego

47. **eSocial API**
    - URL: https://www.gov.br/esocial/
    - Função: Substituiu RAIS e CAGED
    - Dados: Admissões, demissões, folha de pagamento
    - Status: 🔍 PESQUISAR ACESSO
    - Prioridade: 🔥 ALTA

48. **API CAGED (Legado)** ⚠️ DESCONTINUADO
    - Função: Microdados via FTP
    - Status: Substituído por eSocial

49. **API RAIS (Legado)** ⚠️ DESCONTINUADO
    - Função: Microdados via FTP
    - Status: Substituído por eSocial

50. **API Seguro-Desemprego**
    - Função: Consulta benefícios
    - Prioridade: ALTA
    - Status: 🔍 PESQUISAR

51. **API Relação Trabalhista (CNIS)**
    - URL: https://www.gov.br/conecta/catalogo/apis/relacao-trabalhista
    - Função: Cadastro Nacional de Informações Sociais
    - Operador: Dataprev
    - Acesso: ⚠️ Apenas órgãos públicos federais
    - Prioridade: ALTA

### Ministério da Previdência Social (INSS)

52. **API Benefícios Previdenciários**
    - URL: https://www.gov.br/conecta/catalogo/apis/api-beneficios-previdenciarios
    - Função: Consulta benefícios INSS
    - Operador: Dataprev
    - Acesso: ⚠️ Apenas órgãos públicos federais
    - Prioridade: 🔥 ALTA

53. **API INSS - Qualificação Cadastral**
    - Função: Validação de dados previdenciários
    - Operador: Dataprev
    - Prioridade: ALTA

### Ministério da Infraestrutura / DENATRAN

54. **WSDenatran - Veículos, Condutores e Infrações**
    - URL: https://www.gov.br/conecta/catalogo/apis/wsdenatran
    - Função: CNH, veículos, RENAVAM, multas
    - Sistemas: SENATRAN, RENAVAM, RENAVE, RENAJUD, BIN Roubo/Furto
    - Prioridade: 🔥 ALTA

55. **API DETRAN (por estado)**
    - Função: Dados estaduais de trânsito
    - Status: 27 estados com sistemas próprios
    - Prioridade: MÉDIA

### Ministério do Desenvolvimento Social

56. **API Bolsa Família / Cadastro Único**
    - Função: Programas sociais
    - Operador: CAIXA
    - Prioridade: 🔥 ALTA
    - Status: 🔍 PESQUISAR

57. **API Benefícios Sociais (CAIXA)**
    - Função: Consulta múltiplos benefícios
    - Prioridade: ALTA

### Caixa Econômica Federal

58. **API FGTS**
    - Função: Consulta saldo FGTS
    - Prioridade: ALTA
    - Status: 🔍 PESQUISAR

59. **API PIS/PASEP**
    - Função: Abono salarial
    - Prioridade: ALTA

60. **API Habitação (Minha Casa Minha Vida)**
    - Prioridade: MÉDIA

### Tribunal Superior Eleitoral (TSE)

61. **API Dados Eleitorais**
    - URL: https://dadosabertos.tse.jus.br/
    - Função: Eleições, candidatos, doações, resultados
    - Prioridade: 🔥 ALTA (FASE 2)
    - Status: ⏳ PRIORIZADO

### Tesouro Nacional

62. **API SICONFI - Estados e Municípios**
    - URL: https://siconfi.tesouro.gov.br/
    - Função: Finanças públicas subnacionais
    - Dados: RREO, RGF, balanços
    - Prioridade: 🔥 ALTA (FASE 2)
    - Status: ⏳ PRIORIZADO

63. **API SIAFI**
    - Função: Sistema de Administração Financeira Federal
    - Prioridade: ALTA

### Registro Civil (Cartórios)

64. **CRC Nacional - Central de Registro Civil**
    - URL: https://www.registrocivil.org.br/
    - Função: Certidões de nascimento, casamento, óbito
    - Operador: Arpen-Brasil
    - Prioridade: ALTA

65. **ON-RCPN - Operador Nacional Registro Civil**
    - URL: https://onrcpn.org.br/
    - Função: API para certidões eletrônicas
    - Endpoints: Obter Pedidos, Enviar Pedidos, E-Proclamas
    - Prioridade: ALTA

### Agências Reguladoras

66. **ANATEL - Agência Nacional de Telecomunicações**
    - Função: Dados de telecomunicações
    - Prioridade: BAIXA

67. **ANP - Agência Nacional do Petróleo**
    - Função: Preços combustíveis
    - Prioridade: BAIXA

68. **ANEEL - Agência Nacional de Energia Elétrica**
    - Função: Tarifas e consumo de energia
    - Prioridade: BAIXA

69. **ANVISA - Agência Nacional de Vigilância Sanitária**
    - Função: Medicamentos, alimentos
    - Prioridade: BAIXA

### Outros Órgãos Federais

70. **API Câmara dos Deputados**
    - URL: https://dadosabertos.camara.leg.br/
    - Função: Deputados, proposições, votações
    - Prioridade: ALTA

71. **API Senado Federal**
    - URL: https://www12.senado.leg.br/dados-abertos
    - Função: Senadores, projetos de lei
    - Prioridade: ALTA

72. **API STF - Supremo Tribunal Federal**
    - Função: Processos, julgamentos
    - Prioridade: MÉDIA

73. **API IBAMA**
    - Função: Licenças ambientais, multas
    - Prioridade: BAIXA

74. **API INCRA**
    - Função: Reforma agrária, imóveis rurais
    - Prioridade: BAIXA

---

## 🗺️ PARTE 4: APIs ESTADUAIS

### Tribunais de Contas Estaduais (27 estados)

**Integrados (6)**:
- TCE-SP ✅
- TCE-RJ ✅
- TCE-MG ✅
- TCE-BA ✅
- TCE-CE ✅
- TCE-PE ✅

**Pendentes (21 estados)**: AC, AL, AM, AP, DF, ES, GO, MA, MS, MT, PA, PB, PI, PR, RN, RO, RR, RS, SC, SE, TO

### Outros Sistemas Estaduais

75-100. **APIs de Portais da Transparência Estaduais** (27 estados)
101-127. **APIs de Fazenda Estadual** (NFe, ICMS - 27 estados)
128-154. **APIs de DETRAN Estadual** (27 estados)

---

## 🏙️ PARTE 5: APIs MUNICIPAIS

Estimativa: **100+ APIs municipais**
- Portais da Transparência
- Notas Fiscais de Serviço (NFSe)
- IPTU e ISS
- Sistemas de Saúde (SMS)
- Educação Municipal

---

## 📊 ANÁLISE DE PRIORIZAÇÃO

### 🔥 PRIORIDADE CRÍTICA (15 APIs)

1. ✅ **Minha Receita (CNPJ)** - INTEGRADO
2. ✅ **Banco Central (SELIC, PIX, Câmbio)** - INTEGRADO
3. ✅ **PNCP (Licitações)** - INTEGRADO
4. ✅ **Compras.gov.br** - INTEGRADO
5. **Acesso gov.br (Login Único)** - Autenticação
6. **CNS (Cartão Nacional de Saúde)** - Saúde
7. **RNDS (Rede Nacional de Dados em Saúde)** - Saúde
8. **Certidão de Antecedentes Criminais** - Justiça
9. **Cadastro Base de Endereço (CEP)** - Infraestrutura
10. **CND (Certidão Negativa de Débitos)** - Tributário
11. **eSocial** - Trabalho
12. **Benefícios Previdenciários (INSS)** - Previdência
13. **WSDenatran (CNH, Veículos)** - Trânsito
14. **Bolsa Família / Cadastro Único** - Social
15. **TSE (Dados Eleitorais)** - Democracia

### ⚡ ALTA PRIORIDADE (10 APIs)

16. **SICONFI (Tesouro)** - Finanças Subnacionais
17. **Registro Civil (CRC Nacional)** - Documentos
18. **FGTS (CAIXA)** - Trabalhista
19. **PIS/PASEP (CAIXA)** - Social
20. **Relação Trabalhista (CNIS)** - Trabalho
21. **SIAPE (Servidores)** - Gestão Pública
22. **Câmara dos Deputados** - Legislativo
23. **Senado Federal** - Legislativo
24. **Publicar DOU** - Oficial
25. **Fala.Br (Ouvidorias)** - Participação

---

## 💰 ANÁLISE ECONÔMICA

### APIs Gratuitas (Maioria)
- Todas as APIs do Catálogo Conecta
- IBGE, DataSUS, INEP
- PNCP, Compras.gov.br
- Minha Receita
- Banco Central
- TSE, Câmara, Senado

### APIs Pagas (SERPRO)
- Consulta CPF Oficial: R$ X por consulta
- Consulta CNPJ Oficial: R$ X por consulta
- Consulta NFe: R$ X por consulta
- Datavalid: R$ X por validação

**Alternativa Viável**: Usar APIs gratuitas equivalentes
- ✅ Minha Receita (substitui CNPJ pago)
- ⏸️ Aguardar CNS público para CPF

---

## 🎯 RECOMENDAÇÃO ESTRATÉGICA

### FASE 2 (4-6 semanas)
**Integrar 15 APIs Críticas**:
1. TSE (Dados Eleitorais)
2. SICONFI (Finanças Subnacionais)
3. Acesso gov.br (Login Único)
4. CNS (Cartão Saúde)
5. RNDS (Rede Saúde)
6. Certidão Antecedentes
7. Cadastro CEP
8. CND (Certidão Débitos)
9. eSocial
10. Benefícios INSS
11. WSDenatran (Trânsito)
12. Bolsa Família
13. Registro Civil
14. Câmara dos Deputados
15. Senado Federal

### FASE 3 (2-3 meses)
**Expandir para 40+ APIs**:
- 10 APIs Alta Prioridade
- 15 APIs complementares

### FASE 4 (6 meses)
**Cobertura Completa**:
- 100+ APIs integradas
- Cobertura estadual completa
- Principais municípios

---

## 📝 CONCLUSÃO

O Brasil possui um **ecossistema robusto de APIs governamentais**:
- **200+ APIs identificadas**
- **17 integradas** (8.5% de cobertura)
- **183+ pendentes** (91.5%)

**Oportunidade Enorme**: Aumentar de 17 para 100+ APIs em 6 meses.

**Cidadão.AI tem potencial** para ser a **plataforma mais completa de integração de dados públicos brasileiros**.

---

**Próxima Atualização**: 2025-11-14
**Responsável**: Anderson Henrique da Silva
