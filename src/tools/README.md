# 🔧 Cidadão.AI Data Models & Integration Tools

## 📋 Overview

The **Tools & Models** module provides comprehensive **data models** for Brazilian government transparency data and **integration tools** for accessing external APIs. This module handles the complex task of **standardizing** heterogeneous government data formats into unified, type-safe Python models.

## 🏗️ Architecture

```
src/tools/
├── transparency_models.py    # Pydantic models for government data
├── transparency_api.py       # Portal da Transparência integration
├── data_integrator.py       # Multi-source data integration
├── data_visualizer.py       # Data visualization utilities
└── ai_analyzer.py           # AI-powered data analysis tools
```

## 📊 Data Models (transparency_models.py)

### Core Government Data Entities

The system defines **6 primary data models** representing different types of Brazilian government transparency data:

### 1. **Organization** - Government Entities
```python
class Organization(BaseModel):
    codigo: Optional[str]        # Organization code (e.g., "20000")
    nome: Optional[str]          # Full name
    sigla: Optional[str]         # Acronym (e.g., "MS" for Ministry of Health)
    descricao: Optional[str]     # Organization description

# Examples
Ministry of Health: {"codigo": "20000", "nome": "Ministério da Saúde", "sigla": "MS"}
Federal Revenue: {"codigo": "26000", "nome": "Receita Federal", "sigla": "RFB"}
```

### 2. **Supplier** - Government Contractors
```python
class Supplier(BaseModel):
    cnpj: Optional[str]          # Corporate tax ID (14 digits)
    cpf: Optional[str]           # Individual tax ID (11 digits)
    nome: Optional[str]          # Name/Corporate name
    razao_social: Optional[str]  # Legal corporate name
    municipio: Optional[str]     # Municipality
    uf: Optional[str]            # State (2-letter code)
    
    # Automatic validation and cleaning
    @validator('cnpj', 'cpf')
    def validate_document_format(cls, v):
        # Removes formatting: "12.345.678/0001-90" -> "12345678000190"
        # Validates length: CPF=11 digits, CNPJ=14 digits
```

### 3. **Contract** - Government Contracts
```python
class Contract(BaseModel):
    # Identification
    id: Optional[str]                    # Unique contract ID
    numero: Optional[str]                # Contract number
    ano: Optional[int]                   # Year
    mes: Optional[int]                   # Month
    
    # Timeline
    data_assinatura: Optional[date]      # Signature date
    data_inicio_vigencia: Optional[date] # Start date
    data_fim_vigencia: Optional[date]    # End date
    data_publicacao: Optional[date]      # Publication date
    
    # Financial (using Decimal for precision)
    valor_inicial: Optional[Decimal]     # Initial value
    valor_global: Optional[Decimal]      # Total value
    valor_acumulado: Optional[Decimal]   # Accumulated payments
    
    # Description & Classification
    objeto: Optional[str]                # Contract purpose
    objeto_resumido: Optional[str]       # Summary
    modalidade_contratacao: Optional[str] # Contracting method
    modalidade_licitacao: Optional[str]  # Bidding method
    situacao: Optional[str]              # Status
    fundamento_legal: Optional[str]      # Legal basis
    
    # Relationships
    orgao: Optional[Organization]        # Contracting organization
    fornecedor: Optional[Supplier]       # Contractor
```

**Key Features:**
- **Multi-format date parsing**: Handles "DD/MM/YYYY", "YYYY-MM-DD", "DD-MM-YYYY"
- **Decimal precision**: Financial values use `Decimal` to avoid floating-point errors
- **Automatic validation**: Invalid dates/numbers become `None` rather than causing errors

### 4. **Expense** - Government Expenditures
```python
class Expense(BaseModel):
    # Identification & Timeline
    id: Optional[str]
    ano: Optional[int]
    mes: Optional[int]
    data_pagamento: Optional[date]       # Payment date
    data_documento: Optional[date]       # Document date
    
    # Financial Workflow (Brazilian government expense process)
    valor: Optional[Decimal]             # Total amount
    valor_empenhado: Optional[Decimal]   # Committed amount (1st stage)
    valor_liquidado: Optional[Decimal]   # Liquidated amount (2nd stage)
    valor_pago: Optional[Decimal]        # Actually paid (3rd stage)
    
    # Budget Classification (Brazilian public budget structure)
    funcao: Optional[str]                # Function (e.g., "Saúde", "Educação")
    subfuncao: Optional[str]             # Subfunction
    programa: Optional[str]              # Government program
    acao: Optional[str]                  # Specific action/project
    elemento_despesa: Optional[str]      # Expense type
    
    # Description & Relationships
    descricao: Optional[str]             # Expense description
    documento: Optional[str]             # Supporting document
    orgao: Optional[Organization]        # Paying organization
    favorecido: Optional[Supplier]       # Beneficiary
```

**Brazilian Budget Process:**
1. **Empenho** (Commitment) - Budget reservation
2. **Liquidação** (Liquidation) - Service/product verification
3. **Pagamento** (Payment) - Actual payment execution

### 5. **Agreement** - Government Agreements (Convênios)
```python
class Agreement(BaseModel):
    # Identification & Timeline
    id: Optional[str]
    numero: Optional[str]
    ano: Optional[int]
    data_assinatura: Optional[date]
    data_inicio_vigencia: Optional[date]
    data_fim_vigencia: Optional[date]
    data_publicacao: Optional[date]
    
    # Financial Structure
    valor_global: Optional[Decimal]      # Total agreement value
    valor_repasse: Optional[Decimal]     # Federal transfer amount
    valor_contrapartida: Optional[Decimal] # Local counterpart amount
    
    # Description & Status
    objeto: Optional[str]                # Agreement purpose
    situacao: Optional[str]              # Current status
    
    # Multi-level Organization Structure
    orgao_superior: Optional[Organization]   # Federal ministry/agency
    orgao_vinculado: Optional[Organization]  # Linked agency
    convenente: Optional[Supplier]           # Agreement partner (state/city/NGO)
```

### 6. **Bidding** - Government Bidding Processes (Licitações)
```python
class Bidding(BaseModel):
    # Identification & Timeline
    id: Optional[str]
    numero: Optional[str]
    ano: Optional[int]
    data_abertura: Optional[date]        # Opening date
    data_homologacao: Optional[date]     # Approval date
    data_publicacao: Optional[date]      # Publication date
    
    # Financial
    valor_estimado: Optional[Decimal]    # Estimated value
    valor_homologado: Optional[Decimal]  # Final approved value
    
    # Classification
    modalidade: Optional[str]            # Bidding type (pregão, concorrência, etc.)
    situacao: Optional[str]              # Status
    tipo: Optional[str]                  # Type (menor preço, melhor técnica, etc.)
    
    # Documentation
    objeto: Optional[str]                # Bidding object
    edital: Optional[str]                # Notice document
    
    # Relationships
    orgao: Optional[Organization]        # Organizing entity
    vencedor: Optional[Supplier]         # Winning bidder
```

**Brazilian Bidding Modalities:**
- **Pregão** - Auction (most common)
- **Concorrência** - Full competition
- **Tomada de Preços** - Price quotation
- **Convite** - Invitation-only
- **Dispensa** - Exemption cases

### 7. **Servant** - Government Employees
```python
class Servant(BaseModel):
    # Identification
    id: Optional[str]
    cpf: Optional[str]                   # Tax ID (anonymized in API)
    nome: Optional[str]                  # Name
    
    # Employment Details
    cargo: Optional[str]                 # Position/job title
    funcao: Optional[str]                # Function
    situacao: Optional[str]              # Employment status
    regime_juridico: Optional[str]       # Legal employment regime
    
    # Compensation
    remuneracao_basica: Optional[Decimal]  # Basic salary
    remuneracao_total: Optional[Decimal]   # Total compensation
    
    # Timeline
    data_ingresso: Optional[date]          # Entry date
    data_diploma_ingresso: Optional[date]  # Appointment date
    
    # Organization
    orgao: Optional[Organization]          # Employing organization
```

### 8. **SanctionedCompany** - Sanctioned Companies
```python
class SanctionedCompany(BaseModel):
    # Identification
    cnpj: Optional[str]                    # Corporate tax ID
    nome: Optional[str]                    # Company name
    razao_social: Optional[str]            # Legal corporate name
    municipio: Optional[str]               # Municipality
    uf: Optional[str]                      # State
    
    # Sanction Details
    tipo_sancao: Optional[str]             # Sanction type
    data_inicio_sancao: Optional[date]     # Sanction start
    data_fim_sancao: Optional[date]        # Sanction end
    data_publicacao: Optional[date]        # Publication date
    
    # Legal Basis
    fundamentacao_legal: Optional[str]     # Legal framework
    descricao_fundamentacao: Optional[str] # Detailed description
    
    # Authority
    orgao_sancionador: Optional[Organization] # Sanctioning authority
```

**Sanction Registries:**
- **CEAF** - Federal Administration Sanction Registry
- **CEIS** - Companies Sanctioned for Improbity Registry  
- **CNEP** - National Registry of Punished Companies
- **CEPIM** - Registry of Maximum Penalty Companies

## 🔄 Data Processing Pipeline

### Model Parsing & Validation
```python
# Automatic data parsing with error handling
def parse_api_data(data: List[Dict[str, Any]], data_type: str) -> List[BaseModel]:
    """
    Intelligent parsing that:
    1. Maps data_type to appropriate model class
    2. Handles parsing errors gracefully
    3. Continues processing even with malformed records
    4. Returns clean, validated models
    """
    
    model_class = MODEL_MAPPING.get(data_type.lower())
    parsed_data = []
    
    for item in data:
        try:
            parsed_item = model_class(**item)
            parsed_data.append(parsed_item)
        except Exception:
            # Log error but continue processing
            continue
    
    return parsed_data

# Model mapping for different data sources
MODEL_MAPPING = {
    'contracts': Contract,
    'contratos': Contract,      # Portuguese
    'expenses': Expense,
    'despesas': Expense,        # Portuguese
    'agreements': Agreement,
    'convenios': Agreement,     # Portuguese
    'biddings': Bidding,
    'licitacoes': Bidding,      # Portuguese
    'servants': Servant,
    'servidores': Servant,      # Portuguese
    'ceaf': SanctionedCompany,
    'ceis': SanctionedCompany,
    'cnep': SanctionedCompany,
}
```

### Data Validation Features

#### 1. **Date Parsing**
```python
@validator('data_assinatura', 'data_inicio_vigencia', 'data_fim_vigencia')
def parse_date(cls, v):
    """Handles multiple Brazilian date formats"""
    if isinstance(v, str):
        formats = ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y']
        for fmt in formats:
            try:
                return datetime.strptime(v, fmt).date()
            except ValueError:
                continue
        return None  # Invalid date becomes None
    return v
```

#### 2. **Financial Value Processing**
```python
@validator('valor_inicial', 'valor_global', 'valor_acumulado')
def parse_decimal(cls, v):
    """Handles Brazilian number formats and ensures precision"""
    if isinstance(v, (int, float)):
        return Decimal(str(v))  # Convert to string first to avoid float precision issues
    elif isinstance(v, str):
        # Handle Brazilian format: "1.234.567,89" -> "1234567.89"
        v = v.replace('.', '').replace(',', '.').replace(' ', '')
        try:
            return Decimal(v)
        except:
            return None
    return v
```

#### 3. **Document Validation**
```python
@validator('cnpj', 'cpf')
def validate_document_format(cls, v):
    """Validates and cleans Brazilian tax documents"""
    if v:
        # Remove formatting: "12.345.678/0001-90" -> "12345678000190"
        v = v.replace('.', '').replace('/', '').replace('-', '').replace(' ', '')
        
        # Validate format
        if v and not v.isdigit():
            return None
        
        # Validate length: CPF=11, CNPJ=14
        if v and len(v) not in [11, 14]:
            return None
    
    return v
```

## 🔗 Integration Tools

### Portal da Transparência API Client
```python
# transparency_api.py provides comprehensive API integration
class TransparencyAPIClient:
    """
    Complete integration with Portal da Transparência API
    
    Features:
    - Automatic authentication with API key
    - Rate limiting and retry logic
    - Async/await support for high performance
    - Comprehensive error handling
    - Response pagination handling
    - Data model automatic parsing
    """
    
    async def get_contracts(
        self,
        filters: Dict[str, Any] = None,
        year: int = None,
        organization: str = None,
        limit: int = 100
    ) -> List[Contract]:
        """Fetch government contracts with intelligent filtering"""
        
    async def get_expenses(
        self,
        filters: Dict[str, Any] = None,
        year: int = None,
        month: int = None,
        organization: str = None
    ) -> List[Expense]:
        """Fetch government expenses with budget classification"""
        
    async def get_agreements(self, **filters) -> List[Agreement]:
        """Fetch government agreements (convênios)"""
        
    async def get_biddings(self, **filters) -> List[Bidding]:
        """Fetch bidding processes"""
        
    async def get_servants(self, **filters) -> List[Servant]:
        """Fetch government employee data"""
        
    async def get_sanctioned_companies(self, **filters) -> List[SanctionedCompany]:
        """Fetch sanctioned company registries"""
```

### Data Integration Patterns
```python
# Multi-source data fetching with error handling
async def fetch_comprehensive_data(
    organization_code: str,
    year: int,
    include_historical: bool = False
) -> Dict[str, List[BaseModel]]:
    """
    Fetch all related data for an organization:
    - Contracts signed
    - Expenses made  
    - Agreements established
    - Bidding processes conducted
    - Employee information
    - Any sanctions received
    """
    
    async with TransparencyAPIClient() as client:
        # Parallel data fetching for performance
        tasks = [
            client.get_contracts(organization=organization_code, year=year),
            client.get_expenses(organization=organization_code, year=year),
            client.get_agreements(organization=organization_code, year=year),
            client.get_biddings(organization=organization_code, year=year),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            'contracts': results[0],
            'expenses': results[1],
            'agreements': results[2],
            'biddings': results[3]
        }
```

## 🎯 Data Quality & Standardization

### Challenges Addressed

#### 1. **Heterogeneous Data Formats**
- **Problem**: Different government systems use different date formats, number formats, field names
- **Solution**: Unified parsing with multiple format support and validation

#### 2. **Incomplete Data**
- **Problem**: API responses often have missing or null fields
- **Solution**: All fields are `Optional` with sensible defaults and null handling

#### 3. **Data Type Inconsistencies**
- **Problem**: Same field might be string in one API, integer in another
- **Solution**: Flexible validators that handle multiple input types

#### 4. **Brazilian-specific Formats**
- **Problem**: Brazilian number format (1.234.567,89), date format (DD/MM/YYYY), tax ID formats
- **Solution**: Custom validators aware of Brazilian conventions

### Data Completeness Handling
```python
# Example of robust data handling
contract_data = {
    "numero": "123/2024",
    "valor_inicial": "1.234.567,89",  # Brazilian format
    "data_assinatura": "15/03/2024",  # DD/MM/YYYY
    "orgao": {"codigo": "20000", "nome": "Ministério da Saúde"},
    "fornecedor": {
        "cnpj": "12.345.678/0001-90",  # With formatting
        "nome": "Empresa Example Ltda"
    }
}

# Parsed result
contract = Contract(**contract_data)
# contract.valor_inicial == Decimal('1234567.89')
# contract.data_assinatura == date(2024, 3, 15)
# contract.fornecedor.cnpj == "12345678000190"
```

## 📊 Usage Examples

### Basic Model Usage
```python
from src.tools.transparency_models import Contract, parse_api_data

# Parse raw API data
raw_contracts = [
    {
        "numero": "001/2024",
        "valor_inicial": "50000.00",
        "data_assinatura": "2024-01-15",
        "objeto": "Aquisição de equipamentos médicos"
    }
]

contracts = parse_api_data(raw_contracts, "contracts")
for contract in contracts:
    print(f"Contract {contract.numero}: R$ {contract.valor_inicial}")
```

### Advanced Integration
```python
from src.tools.transparency_api import TransparencyAPIClient

async def analyze_ministry_contracts():
    """Analyze contracts from Ministry of Health"""
    
    async with TransparencyAPIClient() as client:
        # Fetch 2024 contracts
        contracts = await client.get_contracts(
            organization="20000",  # Ministry of Health
            year=2024,
            limit=1000
        )
        
        # Find high-value contracts
        high_value = [
            c for c in contracts 
            if c.valor_inicial and c.valor_inicial > 1000000
        ]
        
        # Group by supplier
        suppliers = {}
        for contract in high_value:
            if contract.fornecedor and contract.fornecedor.cnpj:
                cnpj = contract.fornecedor.cnpj
                if cnpj not in suppliers:
                    suppliers[cnpj] = []
                suppliers[cnpj].append(contract)
        
        return suppliers
```

### Data Validation Example
```python
# The models handle various edge cases automatically
messy_data = {
    "valor_inicial": "R$ 1.234.567,89",  # With currency symbol
    "data_assinatura": "31/12/2024",     # DD/MM/YYYY
    "cnpj": "12.345.678/0001-90",        # Formatted CNPJ
    "missing_field": None                # Missing/null fields
}

# Still parses successfully
contract = Contract(**messy_data)
# contract.valor_inicial == Decimal('1234567.89')
# contract.data_assinatura == date(2024, 12, 31)
```

## 🚀 Performance Considerations

### Memory Efficiency
- **Decimal vs Float**: Uses `Decimal` for financial precision but with memory overhead
- **Optional Fields**: Reduces memory usage for sparse data
- **Lazy Loading**: Models are lightweight, containing only essential data

### Processing Speed
- **Batch Processing**: Supports processing large datasets efficiently
- **Error Tolerance**: Continues processing even with malformed records
- **Parallel Parsing**: Can be used with `asyncio.gather()` for parallel processing

### Scalability Patterns
```python
# Process large datasets in chunks
async def process_large_dataset(data_source: str, chunk_size: int = 1000):
    """Process government data in manageable chunks"""
    
    async with TransparencyAPIClient() as client:
        offset = 0
        
        while True:
            # Fetch chunk
            chunk = await client.get_data(
                source=data_source,
                limit=chunk_size,
                offset=offset
            )
            
            if not chunk:
                break
                
            # Process chunk
            parsed_chunk = parse_api_data(chunk, data_source)
            yield parsed_chunk
            
            offset += chunk_size
```

---

This comprehensive data modeling system provides a **robust foundation** for handling the complexity and inconsistency of Brazilian government transparency data, enabling reliable analysis and anomaly detection across multiple data sources.