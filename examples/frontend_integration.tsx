/**
 * Frontend Integration Example
 *
 * Este arquivo demonstra como o frontend Next.js pode consumir
 * as investigações armazenadas no Supabase em tempo real.
 */

import { useEffect, useState, useCallback } from 'react'
import { createClient, RealtimeChannel } from '@supabase/supabase-js'

// =============================================================================
// 1. SETUP DO SUPABASE CLIENT
// =============================================================================

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// =============================================================================
// 2. TIPOS TYPESCRIPT
// =============================================================================

interface Investigation {
  id: string
  user_id: string
  session_id?: string
  query: string
  data_source: string
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled'
  current_phase?: string
  progress: number
  anomalies_found: number
  total_records_analyzed: number
  confidence_score?: number
  filters: Record<string, any>
  anomaly_types: string[]
  results: AnomalyResult[]
  summary?: string
  error_message?: string
  created_at: string
  updated_at: string
  started_at?: string
  completed_at?: string
  processing_time_ms?: number
}

interface AnomalyResult {
  anomaly_id: string
  type: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  confidence: number
  description: string
  explanation: string
  affected_records: any[]
  suggested_actions: string[]
  metadata: Record<string, any>
}

// =============================================================================
// 3. HOOK: useInvestigations (Lista de Investigações)
// =============================================================================

export function useInvestigations() {
  const [investigations, setInvestigations] = useState<Investigation[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchInvestigations()
  }, [])

  const fetchInvestigations = async () => {
    try {
      setLoading(true)
      const { data, error } = await supabase
        .from('investigations')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(20)

      if (error) throw error

      setInvestigations(data || [])
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return { investigations, loading, error, refetch: fetchInvestigations }
}

// =============================================================================
// 4. HOOK: useInvestigation (Investigação Específica com Realtime)
// =============================================================================

export function useInvestigation(investigationId: string) {
  const [investigation, setInvestigation] = useState<Investigation | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!investigationId) return

    // Fetch initial data
    const fetchInvestigation = async () => {
      try {
        setLoading(true)
        const { data, error } = await supabase
          .from('investigations')
          .select('*')
          .eq('id', investigationId)
          .single()

        if (error) throw error

        setInvestigation(data)
      } catch (err: any) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchInvestigation()

    // Subscribe to real-time updates
    const channel = supabase
      .channel(`investigation:${investigationId}`)
      .on(
        'postgres_changes',
        {
          event: 'UPDATE',
          schema: 'public',
          table: 'investigations',
          filter: `id=eq.${investigationId}`,
        },
        (payload) => {
          console.log('Investigation updated in realtime:', payload.new)
          setInvestigation(payload.new as Investigation)
        }
      )
      .subscribe()

    // Cleanup
    return () => {
      supabase.removeChannel(channel)
    }
  }, [investigationId])

  return { investigation, loading, error }
}

// =============================================================================
// 5. HOOK: useInvestigationStats (Estatísticas do Usuário)
// =============================================================================

export function useInvestigationStats(userId: string) {
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!userId) return

    const fetchStats = async () => {
      const { data, error } = await supabase.rpc('get_investigation_stats', {
        p_user_id: userId,
      })

      if (!error && data) {
        setStats(data[0])
      }
      setLoading(false)
    }

    fetchStats()
  }, [userId])

  return { stats, loading }
}

// =============================================================================
// 6. API SERVICE: Criar Nova Investigação
// =============================================================================

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function createInvestigation(params: {
  query: string
  data_source: string
  filters?: Record<string, any>
  anomaly_types?: string[]
  include_explanations?: boolean
}): Promise<{ investigation_id: string; status: string }> {
  // Get user session
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session) {
    throw new Error('User not authenticated')
  }

  const response = await fetch(`${API_URL}/api/v1/investigations/start`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${session.access_token}`,
    },
    body: JSON.stringify(params),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to create investigation')
  }

  return await response.json()
}

// =============================================================================
// 7. COMPONENTE: InvestigationList
// =============================================================================

export function InvestigationList() {
  const { investigations, loading, error } = useInvestigations()

  if (loading) return <div>Loading investigations...</div>
  if (error) return <div>Error: {error}</div>

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">My Investigations</h2>

      {investigations.length === 0 && (
        <p className="text-gray-500">No investigations yet. Create one to get started!</p>
      )}

      {investigations.map((inv) => (
        <InvestigationCard key={inv.id} investigation={inv} />
      ))}
    </div>
  )
}

// =============================================================================
// 8. COMPONENTE: InvestigationCard
// =============================================================================

function InvestigationCard({ investigation }: { investigation: Investigation }) {
  return (
    <div className="border rounded-lg p-4 shadow-sm hover:shadow-md transition">
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-semibold text-lg">{investigation.query}</h3>
        <StatusBadge status={investigation.status} />
      </div>

      <div className="text-sm text-gray-600 mb-2">
        <span className="mr-4">📊 {investigation.data_source}</span>
        <span className="mr-4">🔍 {investigation.anomalies_found} anomalies</span>
        <span>📈 {investigation.total_records_analyzed} records</span>
      </div>

      {investigation.status === 'processing' && (
        <ProgressBar progress={investigation.progress} phase={investigation.current_phase} />
      )}

      {investigation.confidence_score && (
        <div className="mt-2 text-sm">
          Confidence: {(investigation.confidence_score * 100).toFixed(1)}%
        </div>
      )}

      <div className="mt-3 text-xs text-gray-500">
        Created: {new Date(investigation.created_at).toLocaleString()}
      </div>
    </div>
  )
}

// =============================================================================
// 9. COMPONENTE: InvestigationMonitor (Real-time)
// =============================================================================

export function InvestigationMonitor({ investigationId }: { investigationId: string }) {
  const { investigation, loading, error } = useInvestigation(investigationId)

  if (loading) return <div>Loading...</div>
  if (error) return <div>Error: {error}</div>
  if (!investigation) return <div>Investigation not found</div>

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold mb-2">{investigation.query}</h1>
        <StatusBadge status={investigation.status} />
      </div>

      {/* Progress (if processing) */}
      {investigation.status === 'processing' && (
        <div className="bg-blue-50 p-4 rounded-lg">
          <ProgressBar
            progress={investigation.progress}
            phase={investigation.current_phase}
          />
          <div className="mt-2 text-sm text-gray-700">
            Processing: {investigation.current_phase}
          </div>
        </div>
      )}

      {/* Summary Stats */}
      <div className="grid grid-cols-3 gap-4">
        <StatCard
          label="Anomalies Found"
          value={investigation.anomalies_found}
          icon="🚨"
        />
        <StatCard
          label="Records Analyzed"
          value={investigation.total_records_analyzed}
          icon="📊"
        />
        <StatCard
          label="Confidence"
          value={
            investigation.confidence_score
              ? `${(investigation.confidence_score * 100).toFixed(1)}%`
              : 'N/A'
          }
          icon="📈"
        />
      </div>

      {/* Results (if completed) */}
      {investigation.status === 'completed' && (
        <div>
          <h2 className="text-2xl font-bold mb-4">Results</h2>

          {investigation.summary && (
            <div className="bg-gray-50 p-4 rounded-lg mb-4">
              <h3 className="font-semibold mb-2">Summary</h3>
              <p>{investigation.summary}</p>
            </div>
          )}

          <div className="space-y-4">
            {investigation.results.map((result) => (
              <AnomalyCard key={result.anomaly_id} anomaly={result} />
            ))}
          </div>
        </div>
      )}

      {/* Error (if failed) */}
      {investigation.status === 'failed' && investigation.error_message && (
        <div className="bg-red-50 p-4 rounded-lg text-red-800">
          <strong>Error:</strong> {investigation.error_message}
        </div>
      )}
    </div>
  )
}

// =============================================================================
// 10. COMPONENTES AUXILIARES
// =============================================================================

function StatusBadge({ status }: { status: Investigation['status'] }) {
  const colors = {
    pending: 'bg-yellow-100 text-yellow-800',
    processing: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
    cancelled: 'bg-gray-100 text-gray-800',
  }

  return (
    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${colors[status]}`}>
      {status.toUpperCase()}
    </span>
  )
}

function ProgressBar({ progress, phase }: { progress: number; phase?: string }) {
  const percentage = Math.round(progress * 100)

  return (
    <div className="w-full">
      <div className="flex justify-between mb-1 text-sm">
        <span>{phase || 'Processing'}</span>
        <span>{percentage}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2.5">
        <div
          className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}

function StatCard({ label, value, icon }: { label: string; value: any; icon: string }) {
  return (
    <div className="bg-white border rounded-lg p-4 text-center">
      <div className="text-3xl mb-2">{icon}</div>
      <div className="text-2xl font-bold">{value}</div>
      <div className="text-sm text-gray-600">{label}</div>
    </div>
  )
}

function AnomalyCard({ anomaly }: { anomaly: AnomalyResult }) {
  const severityColors = {
    low: 'border-l-yellow-400 bg-yellow-50',
    medium: 'border-l-orange-400 bg-orange-50',
    high: 'border-l-red-400 bg-red-50',
    critical: 'border-l-red-600 bg-red-100',
  }

  return (
    <div className={`border-l-4 rounded p-4 ${severityColors[anomaly.severity]}`}>
      <div className="flex justify-between items-start mb-2">
        <div>
          <span className="font-semibold text-lg">{anomaly.type.toUpperCase()}</span>
          <span className="ml-2 text-sm text-gray-600">
            {anomaly.severity} severity
          </span>
        </div>
        <span className="text-sm font-mono">
          {(anomaly.confidence * 100).toFixed(0)}% confidence
        </span>
      </div>

      <p className="mb-2">{anomaly.description}</p>

      {anomaly.explanation && (
        <details className="mb-2">
          <summary className="cursor-pointer text-sm text-blue-600 hover:underline">
            View explanation
          </summary>
          <p className="mt-2 text-sm text-gray-700">{anomaly.explanation}</p>
        </details>
      )}

      {anomaly.suggested_actions.length > 0 && (
        <div className="mt-2">
          <strong className="text-sm">Suggested Actions:</strong>
          <ul className="list-disc list-inside text-sm mt-1">
            {anomaly.suggested_actions.map((action, i) => (
              <li key={i}>{action}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

// =============================================================================
// 11. EXEMPLO DE USO EM PÁGINA
// =============================================================================

export default function InvestigationsPage() {
  const [creating, setCreating] = useState(false)

  const handleCreateInvestigation = async () => {
    try {
      setCreating(true)

      const result = await createInvestigation({
        query: 'Contratos acima de R$ 1 milhão em 2024',
        data_source: 'contracts',
        filters: {
          min_value: 1000000,
          year: 2024,
        },
        anomaly_types: ['price', 'vendor', 'temporal'],
        include_explanations: true,
      })

      console.log('Investigation created:', result.investigation_id)

      // Redirecionar para página de monitoramento
      // router.push(`/investigations/${result.investigation_id}`)
    } catch (error: any) {
      console.error('Failed to create investigation:', error.message)
      alert(`Error: ${error.message}`)
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <button
          onClick={handleCreateInvestigation}
          disabled={creating}
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {creating ? 'Creating...' : 'New Investigation'}
        </button>
      </div>

      <InvestigationList />
    </div>
  )
}
