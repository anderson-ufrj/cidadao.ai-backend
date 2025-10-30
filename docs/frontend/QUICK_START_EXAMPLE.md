# Quick Start Example - Investigation Results API

**For**: Frontend Team
**Date**: 2025-10-30
**Status**: ✅ Production Ready

---

## 🚀 Copy-Paste Ready Code

### Complete Working Example (TypeScript/React)

```typescript
// === 1. Type Definitions ===

interface InvestigationResponse {
  investigation_id: string;
  status: 'completed' | 'failed';
  query: string;
  data_source: string;
  started_at: string;
  completed_at: string | null;
  anomalies_found: number;
  total_records_analyzed: number;
  results: Anomaly[];
  summary: string;
  confidence_score: number;
  processing_time: number;
}

interface Anomaly {
  anomaly_type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  confidence: number;
  description: string;
  contract_id?: string;
  metadata?: Record<string, any>;
}

// === 2. API Client ===

const API_BASE_URL = 'https://cidadao-api-production.up.railway.app';

async function createInvestigation(query: string): Promise<string> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/investigations/public/create`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to create investigation: ${response.statusText}`);
  }

  const data = await response.json();
  return data.investigation_id;
}

async function getInvestigationResults(
  investigationId: string
): Promise<InvestigationResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/investigations/public/results/${investigationId}`
  );

  if (response.status === 404) {
    throw new Error('Investigation not found');
  }

  if (response.status === 409) {
    throw new Error('Investigation not yet completed');
  }

  if (!response.ok) {
    throw new Error(`Failed to fetch results: ${response.statusText}`);
  }

  return await response.json();
}

// === 3. Polling with Retry Logic ===

async function pollInvestigationResults(
  investigationId: string,
  options: {
    maxAttempts?: number;
    intervalMs?: number;
    onProgress?: (attempt: number) => void;
  } = {}
): Promise<InvestigationResponse> {
  const { maxAttempts = 30, intervalMs = 2000, onProgress } = options;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    onProgress?.(attempt);

    try {
      const results = await getInvestigationResults(investigationId);
      return results;
    } catch (error) {
      if (error instanceof Error && error.message.includes('not yet completed')) {
        // Still processing, wait and retry
        await new Promise(resolve => setTimeout(resolve, intervalMs));
        continue;
      }

      // Other error, throw immediately
      throw error;
    }
  }

  throw new Error('Timeout: Investigation took too long to complete');
}

// === 4. React Hook ===

import { useState, useEffect } from 'react';

function useInvestigation(query: string | null) {
  const [investigationId, setInvestigationId] = useState<string | null>(null);
  const [results, setResults] = useState<InvestigationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (!query) return;

    let cancelled = false;

    async function runInvestigation() {
      try {
        setLoading(true);
        setError(null);
        setProgress(0);

        // Create investigation
        const id = await createInvestigation(query);
        if (cancelled) return;

        setInvestigationId(id);
        setProgress(10);

        // Poll for results
        const results = await pollInvestigationResults(id, {
          maxAttempts: 30,
          intervalMs: 2000,
          onProgress: (attempt) => {
            if (!cancelled) {
              // Progress: 10% (created) -> 90% (polling) -> 100% (done)
              setProgress(10 + (attempt / 30) * 80);
            }
          }
        });

        if (cancelled) return;

        setResults(results);
        setProgress(100);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Unknown error');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    runInvestigation();

    return () => {
      cancelled = true;
    };
  }, [query]);

  return { investigationId, results, loading, error, progress };
}

// === 5. React Component ===

function InvestigationPage() {
  const [query, setQuery] = useState('');
  const [submittedQuery, setSubmittedQuery] = useState<string | null>(null);

  const { investigationId, results, loading, error, progress } = useInvestigation(submittedQuery);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmittedQuery(query);
  };

  return (
    <div className="investigation-page">
      <h1>Investigação de Contratos</h1>

      {/* Search Form */}
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ex: Analisar contratos de limpeza urbana"
          disabled={loading}
        />
        <button type="submit" disabled={loading || !query}>
          Investigar
        </button>
      </form>

      {/* Loading State */}
      {loading && (
        <div className="loading">
          <div className="spinner" />
          <p>Analisando contratos... {Math.round(progress)}%</p>
          {investigationId && (
            <small>ID: {investigationId}</small>
          )}
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="error">
          <p>Erro: {error}</p>
          <button onClick={() => setSubmittedQuery(query)}>
            Tentar Novamente
          </button>
        </div>
      )}

      {/* Results */}
      {results && !loading && (
        <div className="results">
          <h2>Resultados da Investigação</h2>

          {/* Summary Card */}
          <div className="summary-card">
            <div className="metric">
              <span className="label">Anomalias Encontradas</span>
              <span className="value">{results.anomalies_found}</span>
            </div>
            <div className="metric">
              <span className="label">Contratos Analisados</span>
              <span className="value">{results.total_records_analyzed}</span>
            </div>
            <div className="metric">
              <span className="label">Confiança</span>
              <span className="value">{(results.confidence_score * 100).toFixed(0)}%</span>
            </div>
            <div className="metric">
              <span className="label">Tempo de Processamento</span>
              <span className="value">{results.processing_time.toFixed(1)}s</span>
            </div>
          </div>

          {/* Summary Text */}
          <div className="summary-text">
            <p>{results.summary}</p>
          </div>

          {/* Anomalies List */}
          {results.results.length > 0 ? (
            <div className="anomalies-list">
              <h3>Anomalias Detectadas</h3>
              {results.results.map((anomaly, index) => (
                <div
                  key={index}
                  className={`anomaly-card severity-${anomaly.severity}`}
                >
                  <div className="anomaly-header">
                    <span className="anomaly-type">{anomaly.anomaly_type}</span>
                    <span className="anomaly-severity">{anomaly.severity}</span>
                  </div>
                  <p className="anomaly-description">{anomaly.description}</p>
                  {anomaly.contract_id && (
                    <small className="contract-id">
                      Contrato: {anomaly.contract_id}
                    </small>
                  )}
                  <div className="anomaly-confidence">
                    Confiança: {(anomaly.confidence * 100).toFixed(0)}%
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="no-anomalies">
              <p>✅ Nenhuma anomalia significativa foi detectada.</p>
            </div>
          )}

          {/* Metadata */}
          <div className="metadata">
            <small>
              Investigação ID: {results.investigation_id}<br />
              Iniciada em: {new Date(results.started_at).toLocaleString('pt-BR')}<br />
              Concluída em: {results.completed_at ? new Date(results.completed_at).toLocaleString('pt-BR') : 'N/A'}
            </small>
          </div>
        </div>
      )}
    </div>
  );
}

export default InvestigationPage;
```

---

## 🎨 CSS Styles (Optional)

```css
.investigation-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

form {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
}

input {
  flex: 1;
  padding: 12px;
  font-size: 16px;
  border: 2px solid #ddd;
  border-radius: 8px;
}

button {
  padding: 12px 24px;
  font-size: 16px;
  background: #0070f3;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.loading {
  text-align: center;
  padding: 40px;
}

.spinner {
  width: 40px;
  height: 40px;
  margin: 0 auto 20px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #0070f3;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  padding: 20px;
  background: #fee;
  border: 2px solid #f00;
  border-radius: 8px;
  color: #c00;
}

.summary-card {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.metric {
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
  text-align: center;
}

.metric .label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 8px;
}

.metric .value {
  display: block;
  font-size: 32px;
  font-weight: bold;
  color: #0070f3;
}

.summary-text {
  padding: 20px;
  background: #f0f9ff;
  border-left: 4px solid #0070f3;
  border-radius: 8px;
  margin-bottom: 30px;
}

.anomalies-list {
  margin-top: 30px;
}

.anomaly-card {
  padding: 20px;
  margin-bottom: 15px;
  border-radius: 8px;
  border-left: 4px solid;
}

.anomaly-card.severity-low {
  background: #f0fdf4;
  border-color: #22c55e;
}

.anomaly-card.severity-medium {
  background: #fffbeb;
  border-color: #f59e0b;
}

.anomaly-card.severity-high {
  background: #fef2f2;
  border-color: #ef4444;
}

.anomaly-card.severity-critical {
  background: #fdf2f8;
  border-color: #dc2626;
}

.anomaly-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.anomaly-type {
  font-weight: bold;
  text-transform: uppercase;
  font-size: 12px;
}

.anomaly-severity {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: bold;
  text-transform: uppercase;
}

.no-anomalies {
  padding: 40px;
  text-align: center;
  background: #f0fdf4;
  border-radius: 8px;
  color: #166534;
}

.metadata {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #ddd;
  color: #666;
}
```

---

## 📋 Tested in Production

This code was validated against the real production API:

- ✅ **Real Investigation ID**: `05b01580-5017-46d5-9038-779c0ee5f5d1`
- ✅ **Status**: `completed`
- ✅ **Processing Time**: 15.06 seconds
- ✅ **All Fields Present**: 12/12 fields returned correctly

### Production URLs (Copy-Paste Ready):

```
Create Investigation:
POST https://cidadao-api-production.up.railway.app/api/v1/investigations/public/create

Get Results:
GET https://cidadao-api-production.up.railway.app/api/v1/investigations/public/results/{id}
```

---

## 🔥 Testing the API (curl)

```bash
# 1. Create Investigation
curl -X POST "https://cidadao-api-production.up.railway.app/api/v1/investigations/public/create" \
  -H "Content-Type: application/json" \
  -d '{"query": "Analisar contratos"}'

# Response:
# {
#   "investigation_id": "05b01580-5017-46d5-9038-779c0ee5f5d1",
#   "status": "started",
#   "message": "System investigation queued for processing",
#   "system_user_id": "58050609-2fe2-49a6-a342-7cf66d83d216"
# }

# 2. Wait ~15 seconds, then get results
curl "https://cidadao-api-production.up.railway.app/api/v1/investigations/public/results/05b01580-5017-46d5-9038-779c0ee5f5d1"

# Response: (see full response in PRODUCTION_VALIDATION_RESULTS.md)
```

---

## ⚡ Quick Tips

### 1. Processing Time
- Typical investigation: **15-20 seconds**
- Poll every **2 seconds**
- Timeout after **60 seconds** (30 attempts)

### 2. Error Handling
- **404**: Investigation doesn't exist → show error message
- **409**: Still processing → keep polling
- **500**: Server error → retry with exponential backoff

### 3. User Experience
- Show progress bar during polling
- Display estimated time (15-20s)
- Show investigation ID for reference
- Allow user to bookmark/share results URL

### 4. Performance
- Cache results in localStorage (5 min TTL)
- Debounce search input (500ms)
- Use React.memo for result components

---

## 🎯 Next Steps

1. Copy the code above into your frontend
2. Test with production API
3. Customize UI/styling to match your design
4. Add more features:
   - Export results as PDF/Excel
   - Share via social media
   - Filter/sort anomalies
   - Compare multiple investigations

---

**Questions?** Check:
- Full API Docs: `/docs/frontend/INVESTIGATION_RESULTS_ENDPOINT.md`
- Validation Report: `/docs/frontend/PRODUCTION_VALIDATION_RESULTS.md`
- Production Health: https://cidadao-api-production.up.railway.app/health/

---

**Status**: ✅ Ready to Use
**Last Updated**: 2025-10-30
**Environment**: Production (Railway)
