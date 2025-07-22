# 🧪 API Integration Tests / Testes de Integração da API

> **Comprehensive integration tests for Portal da Transparência API and Cidadão.AI multi-agent system**  
> **Testes de integração abrangentes para a API do Portal da Transparência e sistema multi-agente do Cidadão.AI**

## [English](#english) | [Português](#português)

---

## 🇺🇸 English

### Test Files

#### 🔌 **Connectivity Tests**
- **simple_api_test.py**: Basic API connectivity test
- **test_correct_endpoints.py**: Endpoint configuration validation
- **test_working_api.py**: API functionality validation

#### 🛠️ **Functional Tests**
- **test_transparency_api.py**: Main transparency API functionality tests
- **test_with_required_params.py**: Tests with required parameters
- **test_final_fix.py**: Final API fixes validation

### Running Tests

#### 🔧 **Environment Setup**
```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements/dev.txt

# Set environment variables
export TRANSPARENCY_API_KEY="your_api_key_here"
export API_BASE_URL="https://api.portaldatransparencia.gov.br"
```

#### ⚡ **Quick Test Run**
```bash
# Run all integration tests
pytest tests/integration/api/ -v

# Run specific test file
pytest tests/integration/api/test_transparency_api.py -v
```

---

## 🇧🇷 Português

### Arquivos de Teste

#### 🔌 **Testes de Conectividade**
- **simple_api_test.py**: Teste básico de conectividade com a API
- **test_correct_endpoints.py**: Validação de configuração de endpoints
- **test_working_api.py**: Validação de funcionamento da API

#### 🛠️ **Testes Funcionais**
- **test_transparency_api.py**: Testes principais da funcionalidade da API de transparência
- **test_with_required_params.py**: Testes com parâmetros obrigatórios
- **test_final_fix.py**: Validação de correções finais da API

### Executando os Testes

#### 🔧 **Setup do Ambiente**
```bash
# Instalar dependências de teste
pip install -e ".[dev]"

# Configurar variáveis de ambiente
cp .env.example .env
# Adicionar chave da API do Portal da Transparência
```

### ▶️ **Execução**
```bash
# Executar todos os testes de integração da API
pytest tests/integration/api/ -v

# Executar teste específico
pytest tests/integration/api/test_transparency_api.py -v

# Executar com cobertura
pytest tests/integration/api/ --cov=src.tools --cov-report=html

# Executar testes com marcadores específicos
pytest tests/integration/api/ -m "not slow" -v
```

### 📊 **Testes Paralelos**
```bash
# Executar testes em paralelo (mais rápido)
pytest tests/integration/api/ -n auto

# Executar com timeout
pytest tests/integration/api/ --timeout=30
```

## 📝 Configuração de Testes

### 🔑 **Variáveis de Ambiente Necessárias**
```bash
# .env
TRANSPARENCY_API_KEY=sua_chave_aqui
TRANSPARENCY_API_BASE_URL=https://api.portaldatransparencia.gov.br
GROQ_API_KEY=sua_chave_groq_aqui
```

### 🏷️ **Marcadores de Teste**
- `@pytest.mark.integration`: Testes de integração
- `@pytest.mark.slow`: Testes que demoram mais de 10s
- `@pytest.mark.api`: Testes específicos da API
- `@pytest.mark.smoke`: Testes básicos de funcionamento

## 📈 Cobertura de Testes

Os testes cobrem:

- ✅ **Conectividade da API**: Verificação de endpoints e autenticação
- ✅ **Parsing de Dados**: Validação de modelos Pydantic
- ✅ **Filtros e Parâmetros**: Testes de todos os filtros disponíveis
- ✅ **Rate Limiting**: Verificação de limites de taxa
- ✅ **Error Handling**: Tratamento de erros e retry logic
- ✅ **Data Validation**: Validação de estruturas de dados
- ✅ **Performance**: Testes de tempo de resposta

## 🛡️ Testes de Segurança

### 🔒 **Validações de Segurança**
```bash
# Executar testes de segurança
pytest tests/integration/api/ -m security

# Verificar exposição de chaves API
pytest tests/integration/api/test_security.py
```

## 📋 Estrutura dos Testes

```
tests/integration/api/
├── README.md                    # Este arquivo
├── conftest.py                  # Configurações e fixtures
├── simple_api_test.py          # Testes básicos
├── test_correct_endpoints.py   # Validação de endpoints
├── test_final_fix.py           # Testes de correções
├── test_transparency_api.py    # Testes principais
├── test_with_required_params.py # Testes com parâmetros
├── test_working_api.py         # Validação de funcionamento
└── test_security.py            # Testes de segurança
```

## 📚 Documentação de Referência

- 📖 **API Portal da Transparência**: [Documentação oficial](https://api.portaldatransparencia.gov.br/swagger-ui.html)
- 🏗️ **Arquitetura do Sistema**: [Documentação técnica](../../../docs/documentation.html)
- 🤖 **Sistema Multi-Agente**: [Guia dos agentes](../../../src/agents/README.md)

## 🐛 Troubleshooting

### ❌ **Erros Comuns**

**Erro de Autenticação**:
```bash
# Verificar se a chave API está configurada
echo $TRANSPARENCY_API_KEY
```

**Timeout de Rede**:
```bash
# Aumentar timeout nos testes
pytest tests/integration/api/ --timeout=60
```

**Rate Limiting**:
```bash
# Executar testes com delay
pytest tests/integration/api/ --tb=short -v -s
```

## 🔄 Integração Contínua

Os testes são executados automaticamente no CI/CD:

```yaml
# .github/workflows/tests.yml
- name: Run API Integration Tests
  run: |
    pytest tests/integration/api/ \
      --cov=src.tools \
      --cov-report=xml \
      --junit-xml=test-results.xml
```

## 📞 Suporte

Para questões sobre os testes:
- 🐛 **Issues**: [GitHub Issues](https://github.com/anderson-ufrj/cidadao.ai/issues)
- 💬 **Discussões**: [GitHub Discussions](https://github.com/anderson-ufrj/cidadao.ai/discussions)
- 📧 **Email**: andersonhs27@gmail.com

---

**💡 Dica**: Execute `make test-api` para rodar todos os testes de integração da API com configurações otimizadas.