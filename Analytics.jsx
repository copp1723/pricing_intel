import { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts'
import { TrendingUp, TrendingDown, Target, Award, AlertTriangle } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useToast } from '@/hooks/use-toast'

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8']

export function Analytics({ apiService }) {
  const [analytics, setAnalytics] = useState(null)
  const [matchingStats, setMatchingStats] = useState(null)
  const [topScores, setTopScores] = useState([])
  const [loading, setLoading] = useState(true)
  const { toast } = useToast()

  useEffect(() => {
    loadAnalyticsData()
  }, [])

  const loadAnalyticsData = async () => {
    try {
      setLoading(true)
      
      const [analyticsData, matchingData, topScoresData] = await Promise.all([
        apiService.getAnalytics().catch(() => ({ analytics: null })),
        apiService.getMatchingStats().catch(() => ({ stats: null })),
        apiService.get('/top-scores?limit=10').catch(() => ({ vehicles: [] }))
      ])

      setAnalytics(analyticsData.analytics)
      setMatchingStats(matchingData.stats)
      setTopScores(topScoresData.vehicles || [])

    } catch (error) {
      console.error('Failed to load analytics data:', error)
      toast({
        title: "Error",
        description: "Failed to load analytics data",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const runBatchScoring = async () => {
    try {
      toast({
        title: "Starting Batch Scoring",
        description: "This may take a few minutes...",
      })

      const result = await apiService.post('/batch-calculate', { batch_size: 50 })
      
      toast({
        title: "Batch Scoring Complete",
        description: `Processed ${result.result?.processed || 0} vehicles`,
      })
      
      // Refresh data
      loadAnalyticsData()
    } catch (error) {
      toast({
        title: "Batch Scoring Failed",
        description: error.message,
        variant: "destructive",
      })
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading analytics...</p>
        </div>
      </div>
    )
  }

  // Prepare chart data
  const marketPositionData = analytics?.market_positions?.map(pos => ({
    name: pos.position.replace('_', ' ').toUpperCase(),
    value: pos.count,
    percentage: analytics.scored_vehicles > 0 ? ((pos.count / analytics.scored_vehicles) * 100).toFixed(1) : 0
  })) || []

  const actionData = analytics?.recommended_actions?.map(action => ({
    name: action.action.replace('_', ' ').toUpperCase(),
    count: action.count
  })) || []

  const scoreDistribution = analytics?.score_distribution ? [
    { name: 'Min Score', value: analytics.score_distribution.min_score },
    { name: 'Avg Score', value: analytics.score_distribution.avg_score },
    { name: 'Max Score', value: analytics.score_distribution.max_score }
  ] : []

  const componentAverages = analytics?.component_averages ? [
    { name: 'Price Score', value: analytics.component_averages.avg_price_score || 0 },
    { name: 'Age Score', value: analytics.component_averages.avg_age_score || 0 },
    { name: 'Scarcity Score', value: analytics.component_averages.avg_scarcity_score || 0 }
  ] : []

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
          <p className="text-muted-foreground">
            Pricing and competitive analysis insights
          </p>
        </div>
        <div className="flex space-x-2">
          <Button onClick={runBatchScoring} variant="outline">
            Run Batch Scoring
          </Button>
          <Button onClick={loadAnalyticsData} variant="outline">
            Refresh Data
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Coverage</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {analytics?.coverage_pct?.toFixed(1) || 0}%
            </div>
            <p className="text-xs text-muted-foreground">
              {analytics?.scored_vehicles || 0} of {analytics?.total_vehicles || 0} vehicles
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Score</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {analytics?.score_distribution?.avg_score?.toFixed(1) || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              Range: {analytics?.score_distribution?.min_score?.toFixed(1) || 0} - {analytics?.score_distribution?.max_score?.toFixed(1) || 0}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Matches</CardTitle>
            <Award className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {matchingStats?.total_matches || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              {matchingStats?.vehicles_with_matches || 0} vehicles have matches
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Needs Attention</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {analytics?.market_positions?.filter(p => 
                ['poor', 'below_average'].includes(p.position)
              ).reduce((sum, p) => sum + p.count, 0) || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              Vehicles requiring action
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <Tabs defaultValue="positions" className="space-y-4">
        <TabsList>
          <TabsTrigger value="positions">Market Positions</TabsTrigger>
          <TabsTrigger value="actions">Recommended Actions</TabsTrigger>
          <TabsTrigger value="scores">Score Analysis</TabsTrigger>
          <TabsTrigger value="top">Top Performers</TabsTrigger>
        </TabsList>

        <TabsContent value="positions" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Market Position Distribution</CardTitle>
                <CardDescription>
                  How vehicles are positioned competitively
                </CardDescription>
              </CardHeader>
              <CardContent>
                {marketPositionData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={marketPositionData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percentage }) => `${name}: ${percentage}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {marketPositionData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-[300px] text-muted-foreground">
                    No market position data available
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Position Breakdown</CardTitle>
                <CardDescription>
                  Detailed view of market positions
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {marketPositionData.map((position, index) => (
                    <div key={position.name} className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <div 
                          className="w-3 h-3 rounded-full" 
                          style={{ backgroundColor: COLORS[index % COLORS.length] }}
                        />
                        <span className="text-sm">{position.name}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant="secondary">{position.value}</Badge>
                        <span className="text-xs text-muted-foreground">
                          {position.percentage}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="actions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recommended Actions</CardTitle>
              <CardDescription>
                Actions needed for inventory optimization
              </CardDescription>
            </CardHeader>
            <CardContent>
              {actionData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={actionData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-[300px] text-muted-foreground">
                  No action data available
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="scores" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Score Distribution</CardTitle>
                <CardDescription>
                  Overall scoring statistics
                </CardDescription>
              </CardHeader>
              <CardContent>
                {scoreDistribution.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={scoreDistribution}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="value" fill="#82ca9d" />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-[300px] text-muted-foreground">
                    No score data available
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Component Averages</CardTitle>
                <CardDescription>
                  Average scores by component
                </CardDescription>
              </CardHeader>
              <CardContent>
                {componentAverages.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={componentAverages}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="value" fill="#ffc658" />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-[300px] text-muted-foreground">
                    No component data available
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="top" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Top Performing Vehicles</CardTitle>
              <CardDescription>
                Vehicles with highest competitive scores
              </CardDescription>
            </CardHeader>
            <CardContent>
              {topScores.length > 0 ? (
                <div className="space-y-3">
                  {topScores.map((item, index) => (
                    <div key={item.vehicle.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        <Badge variant="outline">#{index + 1}</Badge>
                        <div>
                          <div className="font-medium">
                            {item.vehicle.year} {item.vehicle.make} {item.vehicle.model}
                          </div>
                          <div className="text-sm text-muted-foreground">
                            VIN: {item.vehicle.vin}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-lg">
                          {item.score.overall_score.toFixed(1)}
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {item.score.market_position?.replace('_', ' ')}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex items-center justify-center py-8 text-muted-foreground">
                  No scored vehicles available
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

