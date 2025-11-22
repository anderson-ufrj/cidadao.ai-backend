# 🆕 New Government APIs to Integrate - 2025-11-14

**Priority**: High - Expand data sources for maximum transparency coverage

## 📊 Research Summary

Total APIs identified: **6 new federal APIs + existing state portals**
Current operational: 19 APIs (7 federal + 12 CKAN state portals)
After integration: **25+ APIs operational**

---

## 🎯 Priority 1: Financial & Fiscal Data

### 1. **SICONFI API** - Tesouro Nacional

**Why Priority**: Provides fiscal data for ALL Brazilian states and municipalities

**Base URL**: `https://apidatalake.tesouro.gov.br/ords/siconfi/tt/`

**Endpoints**:
- `/rreo` - Relatório Resumido da Execução Orçamentária (Budget Execution Summary)
- `/rgf` - Relatório de Gestão Fiscal (Fiscal Management Report)
- `/dca` - Declaração de Contas Anuais (Annual Accounts Statement)
- `/msc` - Matriz de Saldos Contábeis (Accounting Balances Matrix)

**Parameters**:
- `an_exercicio` - Year (e.g., 2024)
- `nr_periodo` - Period number
- `co_tipo_demonstrativo` - Report type
- `no_anexo` - Annex name
- `id_ente` - Entity ID (municipality/state code)

**Data Coverage**:
- 5,570 municipalities
- 27 states + Federal District
- Historical data from 2014+
- Budget execution, fiscal reports, annual accounts

**Example**:
```
GET https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo?an_exercicio=2024&nr_periodo=1&id_ente=3550308
```

**Authentication**: None required (public data)

**Response Format**: JSON (5,000 items per page default)

**Impact**: Multiplies municipal coverage from 644 (TCE-SP only) to 5,570 municipalities!

---

### 2. **Tesouro Direto API** - National Treasury Bonds

**Why Priority**: Economic indicators and public debt data

**Data Provided**:
- Treasury bond prices and yields
- Public debt information
- Investment data

**Status**: API exists but needs endpoint documentation research

---

## 🎯 Priority 2: Entity & Registry Data

### 3. **SERPRO CPF API** - Citizen Registry

**Why Priority**: Validate citizen data for investigations

**API**: Consulta CPF by SERPRO

**New Features (2025)**:
- Nome Social field
- Data de Inscrição field
- Real-time validation with Receita Federal

**Data Provided**:
- CPF validation
- Citizen name (including social name)
- Registration date
- Cadastral status

**Authentication**: Likely requires API key

**Use Case**: Validate public servants, contractors in investigations

**Note**: Minha Receita already provides CNPJ (companies), this adds CPF (individuals)

---

### 4. **INSS Benefits API** - Social Security

**Why Priority**: Track public benefit payments

**API**: API Benefícios Previdenciários (via Conecta)

**Base URL**: Available through gov.br/conecta

**Data Provided**:
- List of benefits by person
- Benefit types and amounts
- Payment demographics
- Geographic distribution

**Coverage**:
- All INSS beneficiaries
- Accident benefits
- Retirement pensions
- Other social security benefits

**Authentication**: Conecta platform credentials required

**Portal**: http://dadosabertos.inss.gov.br/dataset/

---

## 🎯 Priority 3: Sector-Specific Data

### 5. **ANAC Aviation Data** - Civil Aviation

**Why Priority**: Track government aviation contracts and operations

**Portal**: https://www.gov.br/anac/pt-br/acesso-a-informacao/dados-abertos

**Data Categories**:
- Aircraft registry (RAB - Registro Aeronáutico Brasileiro)
- Flight statistics (origin, destination, cargo, passengers)
- Aerodromes
- Air operators
- Safety and certification data

**Format**: CSV, JSON, XLS downloadable datasets

**API**: No REST API documented - would need to implement dataset download/parse

**Use Case**:
- Track government aircraft
- Monitor public sector flight contracts
- Analyze air transportation efficiency

---

### 6. **Conecta API Catalog** - Government API Gateway

**Why Important**: Central catalog with 100+ government APIs

**URL**: https://www.gov.br/conecta/catalogo/

**Categories** (34 available on platform):
- Financial Management (14 APIs)
- Budget Management (11 APIs)
- Control & Transparency (11 APIs)
- Reference Registries (11 APIs)
- Agriculture & Land (9 APIs)
- Citizen Registries (13 APIs)
- Environmental (4 APIs)
- Health (4 APIs)
- Company Registries (4 APIs)

**Access Method**: Platform-based (requires registration)

**Potential**: Unlock 100+ federal APIs through single integration point

---

## 📋 Implementation Priority Order

### Phase 1: Immediate (This Week)
1. ✅ **SICONFI API** - COMPLETED ✅
   - ✅ Implemented client with RREO, RGF, DCA, MSC, Entities endpoints
   - ✅ Tested with São Paulo and other major cities
   - ✅ 85.7% success rate (6/7 endpoints working)
   - ✅ 5,570 municipalities accessible (+765% coverage growth)
   - ✅ Documentation created: `docs/SICONFI_INTEGRATION_STATUS_2025_11_14.md`
   - 🔲 Add to comprehensive test suite (pending)

### Phase 2: High Priority (Next Week)
2. **SERPRO CPF API** - Complete citizen/company data
   - Research authentication requirements
   - Implement validation endpoints
   - Integrate with existing Minha Receita (CNPJ)

3. **INSS Benefits API** - Social security data
   - Register on Conecta platform
   - Implement benefits query endpoints
   - Add caching (benefits data changes infrequently)

### Phase 3: Medium Priority (Following Week)
4. **ANAC Aviation Data** - Sector-specific
   - Implement dataset download/parse
   - Create scheduled updates (data is static CSVs)
   - Add aircraft and flight search

5. **Tesouro Direto API** - Economic indicators
   - Research endpoint documentation
   - Implement bond price queries
   - Integrate with existing BCB economic data

### Phase 4: Strategic (Long-term)
6. **Conecta Platform Integration** - API Gateway
   - Register for platform access
   - Evaluate available APIs
   - Implement high-value endpoints

---

## 🎯 Expected Impact

### Current State
- 19 APIs operational (73% success rate)
- Coverage: Federal 100%, 12 states, 644 municipalities (SP only)

### After Phase 1 (SICONFI)
- 20 APIs operational (77% success rate)
- Coverage: Federal 100%, 12 states, **5,570 municipalities** (+765% growth)

### After Phase 2 (SERPRO + INSS)
- 22 APIs operational (85% success rate)
- Complete citizen + company data
- Social security benefit tracking

### After Phase 3 (ANAC + Tesouro Direto)
- 24 APIs operational (92% success rate)
- Sector-specific aviation data
- Enhanced economic indicators

### After Phase 4 (Conecta)
- 50+ APIs potential
- Full government data integration
- Maximum transparency coverage

---

## 🔧 Technical Considerations

### Authentication
- **SICONFI**: None (public API) ✅
- **SERPRO**: API key required (research needed)
- **INSS**: Conecta credentials required
- **ANAC**: None (public datasets) ✅

### Rate Limits
- **SICONFI**: Not documented (likely generous)
- **Portal da Transparência**: 90 req/min (6:00-23:59), 300 req/min (0:00-5:59)
- Others: To be determined

### Caching Strategy
- **SICONFI fiscal reports**: Long TTL (24h - data is monthly/quarterly)
- **SERPRO CPF**: Medium TTL (1h - validate but cache)
- **INSS benefits**: Long TTL (24h - stable data)
- **ANAC datasets**: Very long TTL (7 days - updated infrequently)

### Data Volume
- **SICONFI**: 5,000 items per page (pagination required)
- **INSS**: Likely paginated
- **ANAC**: Large CSV files (GB range)

---

## 📚 Documentation References

- SICONFI Docs: http://apidatalake.tesouro.gov.br/docs/siconfi/
- Tesouro Nacional APIs: https://www.gov.br/tesouronacional/pt-br/central-de-conteudo/apis
- Conecta Catalog: https://www.gov.br/conecta/catalogo/
- ANAC Open Data: https://www.gov.br/anac/pt-br/acesso-a-informacao/dados-abertos
- INSS Open Data: http://dadosabertos.inss.gov.br/dataset/
- Portal da Transparência: https://portaldatransparencia.gov.br/api-de-dados

---

## ✅ Next Steps

1. **Start with SICONFI** (highest impact, no auth required)
2. Create `src/services/transparency_apis/federal_apis/siconfi_client.py`
3. Implement RREO, RGF, DCA, MSC endpoints
4. Add Pydantic models for responses
5. Test with major municipalities (São Paulo, Rio, Brasília)
6. Add to comprehensive test suite
7. Update documentation

**Goal**: Add 1-2 new APIs per week until Phase 4 complete
