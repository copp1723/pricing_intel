import { useState, useEffect } from 'react'
import { 
  Car, 
  TrendingUp, 
  DollarSign, 
  Target,
  AlertTriangle,
  CheckCircle,
  Clock,
  BarChart3
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { useToast } from '@/hooks/use-toast'

export function Dashboard({ systemStats, apiService }) {
  const [analytics, setAnalytics] = useState(null)
  const [matchingStats, setMatchingStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [recentActivity, setRecentActivity] = useState([])
  const { toast } = useToast()

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      
      const [analyticsData, matchingData] = await Promise.all([
        apiService.getAnalytics().catch(() => ({ analytics: null })),
        apiService.getMatchingStats().catch(() => ({ stats: null }))
      ])

      setAnalytics(analyticsData.analytics)
      setMatchingStats(matchingData.stats)
      
      // Simulate recent activity
      setRecentActivity([
        { type: 'score', message: 'Calculated pricing score for 2020 Hyundai Sonata', time: '2 minutes ago' },
        { type: 'match', message: 'Found 5 comparable vehicles for inventory analysis', time: '15 minutes ago' },
        { type: 'insight', message: 'Generated AI insights for market positioning', time: '1 hour ago' },
        { type: 'data', message: 'Processed 363 vehicle records from CSV upload', time: '2 hours ago' }
      ])

    } catch (error) {
      console.error('Failed to load dashboard data:', error)
      toast({
        title: "Error",
        description: "Failed to load dashboard data",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const runQuickTest = async () => {
    try {
      toast({
        title: "Running Tests",
        description: "Testing scoring and insights systems...",
      })

      const [scoringTest, insightsTest] = await Promise.all([
        apiService.testScoring({ sample_size: 3 }),
        apiService.testInsights({ sample_size: 2 })
      ])

      toast({
        title: "Tests Completed",
        description: `Scoring: ${scoringTest.test_results?.length || 0} vehicles, Insights: ${insightsTest.test_results?.length || 0} vehicles`,
      })

      // Refresh data after test
      loadDashboardData()
    } catch (error) {
      toast({
        title: "Test Failed",
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
          <p className="text-muted-foreground">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  const totalVehicles = systemStats?.total_vehicles || 0
  const scoredVehicles = analytics?.scored_vehicles || 0
  const avgScore = analytics?.score_distribution?.avg_score || 0
  const coveragePercent = analytics?.coverage_pct || 0

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Competitive pricing intelligence overview
          </p>
        </div>
        <div className="flex space-x-2">
          <Button onClick={runQuickTest} variant="outline">
            <BarChart3 className="w-4 h-4 mr-2" />
            Run Quick Test
          </Button>
          <Button onClick={loadDashboardData} variant="outline">
            Refresh Data
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Vehicles</CardTitle>
            <Car className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalVehicles.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              Across {systemStats?.unique_makes || 0} makes
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Scored Vehicles</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{scoredVehicles}</div>
            <div className="flex items-center space-x-2">
              <Progress value={coveragePercent} className="flex-1 h-2" />
              <span className="text-xs text-muted-foreground">
                {coveragePercent.toFixed(1)}%
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Score</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{avgScore.toFixed(1)}</div>
            <p className="text-xs text-muted-foreground">
              Out of 100 points
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Price</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${Math.round(systemStats?.price_range?.avg || 0).toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground">
              Range: ${Math.round(systemStats?.price_range?.min || 0).toLocaleString()} - ${Math.round(systemStats?.price_range?.max || 0).toLocaleString()}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Market Positions & Actions */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Market Positions</CardTitle>
            <CardDescription>
              Distribution of vehicle competitive positions
            </CardDescription>
          </CardHeader>
          <CardContent>
            {analytics?.market_positions?.length > 0 ? (
              <div className="space-y-3">
                {analytics.market_positions.map((position) => (
                  <div key={position.position} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {position.position === 'excellent' && <CheckCircle className="w-4 h-4 text-green-500" />}
                      {position.position === 'competitive' && <TrendingUp className="w-4 h-4 text-blue-500" />}
                      {position.position === 'average' && <Target className="w-4 h-4 text-yellow-500" />}
                      {position.position === 'below_average' && <AlertTriangle className="w-4 h-4 text-orange-500" />}
                      {position.position === 'poor' && <AlertTriangle className="w-4 h-4 text-red-500" />}
                      <span className="text-sm capitalize">
                        {position.position.replace('_', ' ')}
                      </span>
                    </div>
                    <Badge variant="secondary">{position.count}</Badge>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">
                No market position data available. Run scoring analysis to see results.
              </p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recommended Actions</CardTitle>
            <CardDescription>
              Actions needed for inventory optimization
            </CardDescription>
          </CardHeader>
          <CardContent>
            {analytics?.recommended_actions?.length > 0 ? (
              <div className="space-y-3">
                {analytics.recommended_actions.map((action) => (
                  <div key={action.action} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Clock className="w-4 h-4 text-muted-foreground" />
                      <span className="text-sm capitalize">
                        {action.action.replace('_', ' ')}
                      </span>
                    </div>
                    <Badge variant="outline">{action.count}</Badge>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">
                No action recommendations available. Calculate scores to see recommendations.
              </p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* System Status & Recent Activity */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>System Status</CardTitle>
            <CardDescription>
              Current system performance and capabilities
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm">Data Ingestion</span>
                <Badge className="bg-green-100 text-green-800">
                  <CheckCircle className="w-3 h-3 mr-1" />
                  Active
                </Badge>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm">Vehicle Matching</span>
                <Badge className="bg-green-100 text-green-800">
                  <CheckCircle className="w-3 h-3 mr-1" />
                  Active
                </Badge>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm">Pricing Scoring</span>
                <Badge className="bg-green-100 text-green-800">
                  <CheckCircle className="w-3 h-3 mr-1" />
                  Active
                </Badge>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm">AI Insights</span>
                <Badge className="bg-green-100 text-green-800">
                  <CheckCircle className="w-3 h-3 mr-1" />
                  Active
                </Badge>
              </div>

              {matchingStats && (
                <div className="pt-2 border-t">
                  <div className="text-xs text-muted-foreground space-y-1">
                    <div>Total matches: {matchingStats.total_matches || 0}</div>
                    <div>Vehicles with matches: {matchingStats.vehicles_with_matches || 0}</div>
                    <div>Avg matches per vehicle: {matchingStats.avg_matches_per_vehicle || 0}</div>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>
              Latest system operations and updates
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {recentActivity.map((activity, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm">{activity.message}</p>
                    <p className="text-xs text-muted-foreground">{activity.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

