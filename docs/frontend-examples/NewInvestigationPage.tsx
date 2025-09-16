// Exemplo de página de Nova Investigação
// /app/investigations/new/page.tsx

"use client"

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Checkbox } from '@/components/ui/checkbox'
import { Calendar } from '@/components/ui/calendar'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { AlertCircle, Calendar as CalendarIcon, Sparkles, Search, TrendingUp } from 'lucide-react'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { toast } from 'sonner'
import { useInvestigationStore } from '@/stores/investigationStore'

// Órgãos principais para investigação
const ORGAOS = [
  { value: '26000', label: 'Ministério da Saúde', risk: 'high' },
  { value: '20000', label: 'Presidência da República', risk: 'medium' },
  { value: '25000', label: 'Ministério da Educação', risk: 'high' },
  { value: '30000', label: 'Ministério da Justiça', risk: 'medium' },
  { value: '22000', label: 'Ministério da Agricultura', risk: 'low' },
]

const ANALYSIS_TYPES = [
  {
    id: 'price_anomalies',
    label: 'Anomalias de Preço',
    description: 'Detecta sobrepreço e superfaturamento',
    icon: '💰'
  },
  {
    id: 'vendor_concentration',
    label: 'Concentração de Fornecedores',
    description: 'Identifica monopólios e cartéis',
    icon: '🏢'
  },
  {
    id: 'temporal_patterns',
    label: 'Padrões Temporais',
    description: 'Analisa gastos suspeitos no tempo',
    icon: '📅'
  },
  {
    id: 'duplicate_contracts',
    label: 'Contratos Duplicados',
    description: 'Encontra fracionamento irregular',
    icon: '📄'
  }
]

export default function NewInvestigationPage() {
  const router = useRouter()
  const { createInvestigation } = useInvestigationStore()
  const [isLoading, setIsLoading] = useState(false)
  
  // Form state
  const [orgao, setOrgao] = useState('')
  const [dateRange, setDateRange] = useState<{ from: Date; to: Date }>({
    from: new Date(2024, 0, 1),
    to: new Date()
  })
  const [selectedAnalysis, setSelectedAnalysis] = useState<string[]>([
    'price_anomalies',
    'vendor_concentration'
  ])
  const [depth, setDepth] = useState<'quick' | 'complete' | 'deep'>('complete')

  const handleSubmit = async () => {
    if (!orgao) {
      toast.error('Selecione um órgão para investigar')
      return
    }

    setIsLoading(true)
    
    try {
      const result = await createInvestigation({
        orgao_codigo: orgao,
        periodo_inicio: format(dateRange.from, 'yyyy-MM-dd'),
        periodo_fim: format(dateRange.to, 'yyyy-MM-dd'),
        tipos_analise: selectedAnalysis,
        profundidade: depth
      })
      
      toast.success('Investigação iniciada! Redirecionando...')
      router.push(`/investigations/${result.id}`)
    } catch (error) {
      toast.error('Erro ao iniciar investigação')
      setIsLoading(false)
    }
  }

  const selectedOrgao = ORGAOS.find(o => o.value === orgao)

  return (
    <div className="container max-w-4xl py-10">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight mb-2">
          Nova Investigação
        </h1>
        <p className="text-muted-foreground">
          Configure os parâmetros para analisar contratos e despesas públicas
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Parâmetros da Investigação
          </CardTitle>
          <CardDescription>
            Nossos agentes de IA irão analisar os dados selecionados em busca de irregularidades
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Seleção de Órgão */}
          <div className="space-y-2">
            <Label htmlFor="orgao">Órgão Governamental</Label>
            <Select value={orgao} onValueChange={setOrgao}>
              <SelectTrigger>
                <SelectValue placeholder="Selecione o órgão a investigar" />
              </SelectTrigger>
              <SelectContent>
                {ORGAOS.map((org) => (
                  <SelectItem key={org.value} value={org.value}>
                    <div className="flex items-center justify-between w-full">
                      <span>{org.label}</span>
                      <Badge 
                        variant={
                          org.risk === 'high' ? 'destructive' : 
                          org.risk === 'medium' ? 'secondary' : 
                          'outline'
                        }
                        className="ml-2"
                      >
                        {org.risk === 'high' ? 'Alto Risco' : 
                         org.risk === 'medium' ? 'Médio Risco' : 
                         'Baixo Risco'}
                      </Badge>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {selectedOrgao?.risk === 'high' && (
              <p className="text-sm text-destructive flex items-center gap-1">
                <AlertCircle className="h-3 w-3" />
                Este órgão tem histórico de irregularidades
              </p>
            )}
          </div>

          {/* Período */}
          <div className="space-y-2">
            <Label>Período de Análise</Label>
            <div className="flex gap-2">
              <Popover>
                <PopoverTrigger asChild>
                  <Button variant="outline" className="flex-1 justify-start">
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {format(dateRange.from, 'dd/MM/yyyy', { locale: ptBR })}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0">
                  <Calendar
                    mode="single"
                    selected={dateRange.from}
                    onSelect={(date) => date && setDateRange({ ...dateRange, from: date })}
                    initialFocus
                  />
                </PopoverContent>
              </Popover>
              <span className="flex items-center px-2">até</span>
              <Popover>
                <PopoverTrigger asChild>
                  <Button variant="outline" className="flex-1 justify-start">
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {format(dateRange.to, 'dd/MM/yyyy', { locale: ptBR })}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0">
                  <Calendar
                    mode="single"
                    selected={dateRange.to}
                    onSelect={(date) => date && setDateRange({ ...dateRange, to: date })}
                    initialFocus
                  />
                </PopoverContent>
              </Popover>
            </div>
          </div>

          {/* Tipos de Análise */}
          <div className="space-y-2">
            <Label>Tipos de Análise</Label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {ANALYSIS_TYPES.map((type) => (
                <Card 
                  key={type.id}
                  className={`cursor-pointer transition-colors ${
                    selectedAnalysis.includes(type.id) 
                      ? 'border-primary bg-primary/5' 
                      : 'hover:bg-muted/50'
                  }`}
                  onClick={() => {
                    setSelectedAnalysis(
                      selectedAnalysis.includes(type.id)
                        ? selectedAnalysis.filter(id => id !== type.id)
                        : [...selectedAnalysis, type.id]
                    )
                  }}
                >
                  <CardContent className="flex items-start gap-3 p-4">
                    <Checkbox 
                      checked={selectedAnalysis.includes(type.id)}
                      onCheckedChange={() => {}}
                      className="mt-1"
                    />
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-lg">{type.icon}</span>
                        <span className="font-medium">{type.label}</span>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {type.description}
                      </p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Profundidade */}
          <div className="space-y-2">
            <Label>Profundidade da Análise</Label>
            <div className="grid grid-cols-3 gap-2">
              <Button
                variant={depth === 'quick' ? 'default' : 'outline'}
                onClick={() => setDepth('quick')}
                className="relative"
              >
                Rápida
                <span className="text-xs absolute -top-1 -right-1 bg-green-500 text-white px-1 rounded">
                  ~2min
                </span>
              </Button>
              <Button
                variant={depth === 'complete' ? 'default' : 'outline'}
                onClick={() => setDepth('complete')}
                className="relative"
              >
                Completa
                <span className="text-xs absolute -top-1 -right-1 bg-blue-500 text-white px-1 rounded">
                  ~5min
                </span>
              </Button>
              <Button
                variant={depth === 'deep' ? 'default' : 'outline'}
                onClick={() => setDepth('deep')}
                className="relative"
              >
                Profunda
                <span className="text-xs absolute -top-1 -right-1 bg-purple-500 text-white px-1 rounded">
                  ~10min
                </span>
              </Button>
            </div>
          </div>

          {/* Preview */}
          {orgao && selectedAnalysis.length > 0 && (
            <Card className="bg-muted/30 border-dashed">
              <CardContent className="pt-6">
                <h4 className="font-medium mb-2 flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-primary" />
                  Prévia da Investigação
                </h4>
                <ul className="text-sm space-y-1 text-muted-foreground">
                  <li>• Analisando contratos do(a) <strong>{selectedOrgao?.label}</strong></li>
                  <li>• Período: {format(dateRange.from, 'MMMM/yyyy', { locale: ptBR })} até {format(dateRange.to, 'MMMM/yyyy', { locale: ptBR })}</li>
                  <li>• {selectedAnalysis.length} tipos de análise selecionados</li>
                  <li>• Tempo estimado: {
                    depth === 'quick' ? '~2 minutos' :
                    depth === 'complete' ? '~5 minutos' :
                    '~10 minutos'
                  }</li>
                </ul>
              </CardContent>
            </Card>
          )}

          {/* Botão de Submit */}
          <Button 
            onClick={handleSubmit} 
            disabled={isLoading || !orgao || selectedAnalysis.length === 0}
            size="lg"
            className="w-full"
          >
            {isLoading ? (
              <>
                <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-background border-t-transparent" />
                Iniciando Investigação...
              </>
            ) : (
              <>
                <TrendingUp className="mr-2 h-4 w-4" />
                Iniciar Investigação
              </>
            )}
          </Button>

          <p className="text-xs text-center text-muted-foreground">
            Ao iniciar, nossos agentes de IA começarão a análise em tempo real.
            Você poderá acompanhar o progresso na próxima tela.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}