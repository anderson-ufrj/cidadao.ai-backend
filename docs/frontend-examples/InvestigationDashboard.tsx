// Exemplo de Dashboard de Investigação em Tempo Real
// /app/investigations/[id]/page.tsx

"use client"

import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { 
  AlertTriangle, 
  TrendingUp, 
  Users, 
  Calendar,
  FileText,
  Activity,
  AlertCircle,
  CheckCircle,
  Brain,
  Search,
  BarChart3,
  FileWarning
} from 'lucide-react'
import { useInvestigation } from '@/hooks/useInvestigation'
import { 
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ScatterChart, Scatter
} from 'recharts'

// Cores para os gráficos
const COLORS = ['#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6']

// Mock de agentes trabalhando
const AGENT_STATUS = {
  abaporu: { name: 'Abaporu', status: 'completed', message: 'Investigação orquestrada' },
  zumbi: { name: 'Zumbi dos Palmares', status: 'working', message: 'Detectando anomalias...' },
  anita: { name: 'Anita Garibaldi', status: 'waiting', message: 'Aguardando dados' },
  tiradentes: { name: 'Tiradentes', status: 'waiting', message: 'Preparando relatório' }
}

export default function InvestigationDashboard({ params }: { params: { id: string } }) {
  const { investigation, error, isLoading } = useInvestigation(params.id)
  const [activeTab, setActiveTab] = useState('overview')

  // Simulação de progresso (em produção viria via SSE)
  const [progress, setProgress] = useState(0)
  const [findings, setFindings] = useState<any[]>([])
  
  useEffect(() => {
    const interval = setInterval(() => {
      setProgress(p => Math.min(p + 10, 100))
    }, 2000)
    return () => clearInterval(interval)
  }, [])

  if (isLoading) {
    return (
      <div className="container py-10">
        <div className="flex items-center justify-center h-96">
          <div className="text-center space-y-4">
            <div className="h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent mx-auto" />
            <p className="text-muted-foreground">Carregando investigação...</p>
          </div>
        </div>
      </div>
    )
  }

  // Dados mock para visualização
  const priceAnomalies = [
    { name: 'Esperado', value: 50000, actual: 50000 },
    { name: 'Contrato A', value: 45000, actual: 150000 },
    { name: 'Contrato B', value: 80000, actual: 85000 },
    { name: 'Contrato C', value: 120000, actual: 380000 },
    { name: 'Contrato D', value: 60000, actual: 62000 }
  ]

  const vendorConcentration = [
    { name: 'Empresa XYZ Ltda', value: 45, contracts: 23 },
    { name: 'ABC Comércio', value: 22, contracts: 15 },
    { name: 'Tech Solutions', value: 18, contracts: 12 },
    { name: 'Outros', value: 15, contracts: 28 }
  ]

  const temporalData = [
    { month: 'Jan', value: 1200000 },
    { month: 'Fev', value: 980000 },
    { month: 'Mar', value: 1100000 },
    { month: 'Abr', value: 950000 },
    { month: 'Mai', value: 1050000 },
    { month: 'Jun', value: 890000 },
    { month: 'Jul', value: 920000 },
    { month: 'Ago', value: 1080000 },
    { month: 'Set', value: 1150000 },
    { month: 'Out', value: 1320000 },
    { month: 'Nov', value: 1890000 },
    { month: 'Dez', value: 3200000 } // Pico suspeito
  ]

  const riskLevel = progress > 80 ? 'high' : progress > 50 ? 'medium' : 'low'
  const anomaliesCount = Math.floor(progress / 10) + 3

  return (
    <div className="container py-10">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight mb-2">
              Investigação #{params.id}
            </h1>
            <p className="text-muted-foreground">
              Ministério da Saúde • Janeiro a Dezembro 2024
            </p>
          </div>
          <Badge 
            variant={progress === 100 ? 'default' : 'secondary'}
            className="text-lg px-4 py-2"
          >
            {progress === 100 ? 'Concluída' : 'Em Andamento'}
          </Badge>
        </div>
      </div>

      {/* Progress Section */}
      {progress < 100 && (
        <Card className="mb-6">
          <CardContent className="pt-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Progresso da Investigação</span>
                <span className="text-sm text-muted-foreground">{progress}%</span>
              </div>
              <Progress value={progress} className="h-2" />
              
              {/* Agentes Status */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                {Object.entries(AGENT_STATUS).map(([key, agent]) => (
                  <div key={key} className="flex items-center gap-2 text-sm">
                    <div className={`h-2 w-2 rounded-full ${
                      agent.status === 'completed' ? 'bg-green-500' :
                      agent.status === 'working' ? 'bg-blue-500 animate-pulse' :
                      'bg-gray-300'
                    }`} />
                    <span className="font-medium">{agent.name}</span>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Risk Overview */}
      <div className="grid gap-4 md:grid-cols-4 mb-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Nível de Risco</CardTitle>
            <AlertTriangle className={`h-4 w-4 ${
              riskLevel === 'high' ? 'text-red-500' :
              riskLevel === 'medium' ? 'text-yellow-500' :
              'text-green-500'
            }`} />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {riskLevel === 'high' ? 'Alto' :
               riskLevel === 'medium' ? 'Médio' :
               'Baixo'}
            </div>
            <p className="text-xs text-muted-foreground">
              Baseado em {anomaliesCount} anomalias
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Anomalias Detectadas</CardTitle>
            <FileWarning className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{anomaliesCount}</div>
            <p className="text-xs text-muted-foreground">
              Em 342 contratos analisados
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Valor em Risco</CardTitle>
            <TrendingUp className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">R$ 2,3M</div>
            <p className="text-xs text-muted-foreground">
              Possível superfaturamento
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Concentração</CardTitle>
            <Users className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">67%</div>
            <p className="text-xs text-muted-foreground">
              Em 3 fornecedores principais
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Visão Geral</TabsTrigger>
          <TabsTrigger value="anomalies">Anomalias</TabsTrigger>
          <TabsTrigger value="vendors">Fornecedores</TabsTrigger>
          <TabsTrigger value="timeline">Linha do Tempo</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          {/* Alertas Críticos */}
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Alerta Crítico</AlertTitle>
            <AlertDescription>
              Detectamos contratos com sobrepreço de até 300% acima da média de mercado.
              3 fornecedores concentram 67% dos contratos, indicando possível cartelização.
            </AlertDescription>
          </Alert>

          {/* Achados Principais */}
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Principais Achados</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  <li className="flex items-start gap-2">
                    <Badge variant="destructive" className="mt-0.5">Alto</Badge>
                    <div>
                      <p className="font-medium">Sobrepreço Sistemático</p>
                      <p className="text-sm text-muted-foreground">
                        Equipamentos médicos com valores 200-300% acima do mercado
                      </p>
                    </div>
                  </li>
                  <li className="flex items-start gap-2">
                    <Badge variant="secondary" className="mt-0.5">Médio</Badge>
                    <div>
                      <p className="font-medium">Concentração de Fornecedores</p>
                      <p className="text-sm text-muted-foreground">
                        Empresa XYZ Ltda ganhou 45% dos contratos do período
                      </p>
                    </div>
                  </li>
                  <li className="flex items-start gap-2">
                    <Badge variant="secondary" className="mt-0.5">Médio</Badge>
                    <div>
                      <p className="font-medium">Gastos de Fim de Ano</p>
                      <p className="text-sm text-muted-foreground">
                        Dezembro concentrou 35% dos gastos anuais
                      </p>
                    </div>
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Atividade dos Agentes</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {Object.entries(AGENT_STATUS).map(([key, agent]) => (
                    <div key={key} className="flex items-center gap-3">
                      <div className={`h-8 w-8 rounded-full flex items-center justify-center text-xs ${
                        agent.status === 'completed' ? 'bg-green-100 text-green-700' :
                        agent.status === 'working' ? 'bg-blue-100 text-blue-700' :
                        'bg-gray-100 text-gray-500'
                      }`}>
                        {agent.status === 'completed' ? <CheckCircle className="h-4 w-4" /> :
                         agent.status === 'working' ? <Brain className="h-4 w-4 animate-pulse" /> :
                         <Activity className="h-4 w-4" />}
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium">{agent.name}</p>
                        <p className="text-xs text-muted-foreground">{agent.message}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="anomalies" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Anomalias de Preço Detectadas</CardTitle>
              <CardDescription>
                Comparação entre valores esperados e valores contratados
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[400px]">
                <ResponsiveContainer width="100%" height="100%">
                  <ScatterChart>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="value" name="Valor Esperado" 
                           tickFormatter={(value) => `R$ ${(value/1000).toFixed(0)}k`} />
                    <YAxis dataKey="actual" name="Valor Real"
                           tickFormatter={(value) => `R$ ${(value/1000).toFixed(0)}k`} />
                    <Tooltip 
                      formatter={(value: any) => `R$ ${value.toLocaleString('pt-BR')}`}
                      labelFormatter={(label) => `Contrato: ${label}`}
                    />
                    <Scatter name="Contratos" data={priceAnomalies} fill="#ef4444">
                      {priceAnomalies.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={
                          entry.actual > entry.value * 1.5 ? '#ef4444' : '#10b981'
                        } />
                      ))}
                    </Scatter>
                    {/* Linha de referência diagonal */}
                    <Line type="monotone" dataKey="value" stroke="#6b7280" strokeDasharray="5 5" />
                  </ScatterChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="vendors" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Concentração de Fornecedores</CardTitle>
              <CardDescription>
                Distribuição de contratos por fornecedor
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-6">
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={vendorConcentration}
                        dataKey="value"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        outerRadius={100}
                        label={({value}) => `${value}%`}
                      >
                        {vendorConcentration.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                
                <div className="space-y-4">
                  <h4 className="font-medium">Detalhes dos Fornecedores</h4>
                  {vendorConcentration.map((vendor, index) => (
                    <div key={vendor.name} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                      <div className="flex items-center gap-3">
                        <div className="h-3 w-3 rounded-full" style={{ backgroundColor: COLORS[index] }} />
                        <div>
                          <p className="font-medium">{vendor.name}</p>
                          <p className="text-sm text-muted-foreground">{vendor.contracts} contratos</p>
                        </div>
                      </div>
                      <Badge variant={vendor.value > 30 ? 'destructive' : 'secondary'}>
                        {vendor.value}%
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="timeline" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Evolução Temporal dos Gastos</CardTitle>
              <CardDescription>
                Análise mensal dos valores contratados
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[400px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={temporalData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis tickFormatter={(value) => `R$ ${(value/1000000).toFixed(1)}M`} />
                    <Tooltip formatter={(value: any) => `R$ ${value.toLocaleString('pt-BR')}`} />
                    <Bar dataKey="value">
                      {temporalData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={
                          entry.value > 2000000 ? '#ef4444' : '#3b82f6'
                        } />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <Alert className="mt-4">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Padrão Suspeito Detectado</AlertTitle>
                <AlertDescription>
                  Dezembro apresentou gastos 250% acima da média mensal, indicando possível
                  tentativa de esgotar orçamento no fim do exercício.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Action Buttons */}
      {progress === 100 && (
        <div className="mt-6 flex gap-4">
          <Button size="lg" className="flex-1">
            <FileText className="mr-2 h-4 w-4" />
            Gerar Relatório Completo
          </Button>
          <Button size="lg" variant="outline" className="flex-1">
            <BarChart3 className="mr-2 h-4 w-4" />
            Exportar Dados
          </Button>
        </div>
      )}
    </div>
  )
}