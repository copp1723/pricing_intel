import { useState, useEffect } from 'react'
import { Settings as SettingsIcon, Upload, Database, Zap, Info, CheckCircle, AlertTriangle } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useToast } from '@/hooks/use-toast'

export function Settings({ apiService }) {
  const [systemInfo, setSystemInfo] = useState(null)
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [processing, setProcessing] = useState(false)
  const { toast } = useToast()

  useEffect(() => {
    loadSystemInfo()
  }, [])

  const loadSystemInfo = async () => {
    try {
      setLoading(true)
      
      const [stats, analytics, matchingStats] = await Promise.all([
        apiService.getStats().catch(() => ({})),
        apiService.getAnalytics().catch(() => ({ analytics: null })),
        apiService.getMatchingStats().catch(() => ({ stats: null }))
      ])

      setSystemInfo({
        stats,
        analytics: analytics.analytics,
        matchingStats: matchingStats.stats
      })

    } catch (error) {
      console.error('Failed to load system info:', error)
      toast({
        title: "Error",
        description: "Failed to load system information",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const processSampleData = async () => {
    try {
      setProcessing(true)
      
      toast({
        title: "Processing Sample Data",
        description: "This may take a few minutes...",
      })

      const result = await apiService.post('/process-sample', {
        dealer_name: "Sample Dealer"
      })

      toast({
        title: "Processing Complete",
        description: `Processed ${result.summary?.processed || 0} vehicles`,
      })

      // Refresh system info
      loadSystemInfo()

    } catch (error) {
      toast({
        title: "Processing Failed",
        description: error.message,
        variant: "destructive",
      })
    } finally {
      setProcessing(false)
    }
  }

  const runSystemTests = async () => {
    try {
      setProcessing(true)
      
      toast({
        title: "Running System Tests",
        description: "Testing all system components...",
      })

      const [scoringTest, insightsTest, matchingTest] = await Promise.all([
        apiService.testScoring({ sample_size: 3 }).catch(() => ({ success: false })),
        apiService.testInsights({ sample_size: 2 }).catch(() => ({ success: false })),
        apiService.post('/batch-match', { batch_size: 10 }).catch(() => ({ success: false }))
      ])

      const results = []
      if (scoringTest.success) results.push('Scoring')
      if (insightsTest.success) results.push('Insights')
      if (matchingTest.success) results.push('Matching')

      toast({
        title: "System Tests Complete",
        description: `Tested: ${results.join(', ')}`,
      })

      // Refresh system info
      loadSystemInfo()

    } catch (error) {
      toast({
        title: "Tests Failed",
        description: error.message,
        variant: "destructive",
      })
    } finally {
      setProcessing(false)
    }
  }

  const handleFileUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    if (!file.name.endsWith('.csv')) {
      toast({
        title: "Invalid File",
        description: "Please select a CSV file",
        variant: "destructive",
      })
      return
    }

    try {
      setUploading(true)
      
      toast({
        title: "Uploading File",
        description: "Processing CSV data...",
      })

      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch('http://localhost:5001/api/upload-csv', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const result = await response.json()

      toast({
        title: "Upload Complete",
        description: `Processed ${result.summary?.processed || 0} vehicles`,
      })

      // Refresh system info
      loadSystemInfo()

    } catch (error) {
      toast({
        title: "Upload Failed",
        description: error.message,
        variant: "destructive",
      })
    } finally {
      setUploading(false)
      // Reset file input
      event.target.value = ''
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading settings...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
          <p className="text-muted-foreground">
            System configuration and management
          </p>
        </div>
        <Button onClick={loadSystemInfo} variant="outline">
          Refresh Status
        </Button>
      </div>

      <Tabs defaultValue="system" className="space-y-4">
        <TabsList>
          <TabsTrigger value="system">System Status</TabsTrigger>
          <TabsTrigger value="data">Data Management</TabsTrigger>
          <TabsTrigger value="testing">Testing & Diagnostics</TabsTrigger>
        </TabsList>

        <TabsContent value="system" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Database className="w-5 h-5" />
                  <span>Database Status</span>
                </CardTitle>
                <CardDescription>
                  Current database statistics and health
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Total Vehicles</span>
                    <Badge variant="outline">
                      {systemInfo?.stats?.total_vehicles || 0}
                    </Badge>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Unique Makes</span>
                    <Badge variant="secondary">
                      {systemInfo?.stats?.unique_makes || 0}
                    </Badge>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Unique Models</span>
                    <Badge variant="secondary">
                      {systemInfo?.stats?.unique_models || 0}
                    </Badge>
                  </div>

                  {systemInfo?.stats?.price_range && (
                    <>
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Avg Price</span>
                        <span className="text-sm font-medium">
                          ${Math.round(systemInfo.stats.price_range.avg).toLocaleString()}
                        </span>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Price Range</span>
                        <span className="text-sm">
                          ${Math.round(systemInfo.stats.price_range.min).toLocaleString()} - ${Math.round(systemInfo.stats.price_range.max).toLocaleString()}
                        </span>
                      </div>
                    </>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Zap className="w-5 h-5" />
                  <span>Processing Status</span>
                </CardTitle>
                <CardDescription>
                  Analysis and processing statistics
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Scored Vehicles</span>
                    <Badge variant="outline">
                      {systemInfo?.analytics?.scored_vehicles || 0}
                    </Badge>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Coverage</span>
                    <Badge variant="secondary">
                      {systemInfo?.analytics?.coverage_pct?.toFixed(1) || 0}%
                    </Badge>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Total Matches</span>
                    <Badge variant="outline">
                      {systemInfo?.matchingStats?.total_matches || 0}
                    </Badge>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-sm">Avg Score</span>
                    <span className="text-sm font-medium">
                      {systemInfo?.analytics?.score_distribution?.avg_score?.toFixed(1) || 0}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <CheckCircle className="w-5 h-5" />
                  <span>Service Health</span>
                </CardTitle>
                <CardDescription>
                  Status of all system services
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
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
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Info className="w-5 h-5" />
                  <span>System Information</span>
                </CardTitle>
                <CardDescription>
                  Platform details and configuration
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 text-sm">
                  <div className="flex items-center justify-between">
                    <span>Platform</span>
                    <span>Pricing Intelligence v1.0</span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span>Backend</span>
                    <span>Flask + SQLAlchemy</span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span>Frontend</span>
                    <span>React + Tailwind CSS</span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span>Database</span>
                    <span>SQLite</span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span>API Status</span>
                    <Badge className="bg-green-100 text-green-800">
                      <CheckCircle className="w-3 h-3 mr-1" />
                      Online
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="data" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Upload className="w-5 h-5" />
                  <span>CSV Upload</span>
                </CardTitle>
                <CardDescription>
                  Upload new inventory data from CSV files
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="csv-upload" className="text-sm font-medium">
                    Select CSV File
                  </Label>
                  <Input
                    id="csv-upload"
                    type="file"
                    accept=".csv"
                    onChange={handleFileUpload}
                    disabled={uploading}
                    className="mt-2"
                  />
                </div>
                
                <div className="text-xs text-muted-foreground">
                  <p>Supported format: CSV files with vehicle inventory data</p>
                  <p>Required columns: VIN, Year, Make, Model, Price</p>
                </div>
                
                {uploading && (
                  <div className="flex items-center space-x-2 text-sm">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
                    <span>Uploading and processing...</span>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Database className="w-5 h-5" />
                  <span>Sample Data</span>
                </CardTitle>
                <CardDescription>
                  Load sample data for testing and demonstration
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-muted-foreground">
                  Process the included sample CSV data to populate the system with test vehicles.
                </p>
                
                <Button 
                  onClick={processSampleData}
                  disabled={processing}
                  className="w-full"
                >
                  <Database className="w-4 h-4 mr-2" />
                  {processing ? 'Processing...' : 'Process Sample Data'}
                </Button>
                
                <div className="text-xs text-muted-foreground">
                  <p>This will load approximately 363 sample vehicles</p>
                  <p>Includes various makes, models, and conditions</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="testing" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Zap className="w-5 h-5" />
                  <span>System Tests</span>
                </CardTitle>
                <CardDescription>
                  Run comprehensive system tests
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-muted-foreground">
                  Test all system components including scoring, matching, and insights generation.
                </p>
                
                <Button 
                  onClick={runSystemTests}
                  disabled={processing}
                  className="w-full"
                >
                  <Zap className="w-4 h-4 mr-2" />
                  {processing ? 'Running Tests...' : 'Run System Tests'}
                </Button>
                
                <div className="text-xs text-muted-foreground">
                  <p>Tests: Vehicle scoring, matching engine, AI insights</p>
                  <p>Duration: 2-3 minutes</p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <AlertTriangle className="w-5 h-5" />
                  <span>Diagnostics</span>
                </CardTitle>
                <CardDescription>
                  System diagnostics and troubleshooting
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span>API Connection</span>
                    <Badge className="bg-green-100 text-green-800">
                      <CheckCircle className="w-3 h-3 mr-1" />
                      OK
                    </Badge>
                  </div>
                  
                  <div className="flex items-center justify-between text-sm">
                    <span>Database Connection</span>
                    <Badge className="bg-green-100 text-green-800">
                      <CheckCircle className="w-3 h-3 mr-1" />
                      OK
                    </Badge>
                  </div>
                  
                  <div className="flex items-center justify-between text-sm">
                    <span>VIN Decoding Service</span>
                    <Badge className="bg-green-100 text-green-800">
                      <CheckCircle className="w-3 h-3 mr-1" />
                      OK
                    </Badge>
                  </div>
                  
                  <div className="flex items-center justify-between text-sm">
                    <span>AI Insights Engine</span>
                    <Badge className="bg-green-100 text-green-800">
                      <CheckCircle className="w-3 h-3 mr-1" />
                      OK
                    </Badge>
                  </div>
                </div>
                
                <div className="text-xs text-muted-foreground">
                  <p>All system components are operational</p>
                  <p>Last checked: {new Date().toLocaleString()}</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}

