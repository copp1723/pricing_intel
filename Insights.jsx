import { useState, useEffect } from 'react'
import { Brain, Lightbulb, TrendingUp, AlertTriangle, CheckCircle, Eye, Zap } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { useToast } from '@/hooks/use-toast'

export function Insights({ apiService }) {
  const [marketInsights, setMarketInsights] = useState(null)
  const [vehicleInsights, setVehicleInsights] = useState([])
  const [selectedVin, setSelectedVin] = useState('')
  const [selectedInsight, setSelectedInsight] = useState(null)
  const [loading, setLoading] = useState(true)
  const [generatingInsights, setGeneratingInsights] = useState(false)
  const { toast } = useToast()

  useEffect(() => {
    loadInsightsData()
  }, [])

  const loadInsightsData = async () => {
    try {
      setLoading(true)
      
      const marketData = await apiService.getMarketInsights()
      setMarketInsights(marketData.market_insights)

    } catch (error) {
      console.error('Failed to load insights data:', error)
      toast({
        title: "Error",
        description: "Failed to load insights data",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const generateVehicleInsight = async (vin) => {
    if (!vin) {
      toast({
        title: "VIN Required",
        description: "Please enter a VIN to generate insights",
        variant: "destructive",
      })
      return
    }

    try {
      setGeneratingInsights(true)
      
      toast({
        title: "Generating Insights",
        description: "AI is analyzing the vehicle...",
      })

      const result = await apiService.getVehicleInsights(vin)
      
      // Add to vehicle insights list
      setVehicleInsights(prev => {
        const filtered = prev.filter(item => item.vin !== vin)
        return [result.insights, ...filtered].slice(0, 10) // Keep last 10
      })

      toast({
        title: "Insights Generated",
        description: "AI analysis completed successfully",
      })

      setSelectedVin('')
    } catch (error) {
      toast({
        title: "Generation Failed",
        description: error.message,
        variant: "destructive",
      })
    } finally {
      setGeneratingInsights(false)
    }
  }

  const generateBatchInsights = async () => {
    try {
      setGeneratingInsights(true)
      
      toast({
        title: "Generating Batch Insights",
        description: "This may take a few minutes...",
      })

      const result = await apiService.testInsights({ sample_size: 5 })
      
      if (result.test_results) {
        // Convert test results to insights format
        const insights = result.test_results.map(test => ({
          vin: test.vehicle.vin,
          vehicle_id: test.vehicle.id || 1,
          insights: {
            executive_summary: test.executive_summary + '...',
            recommendations: {
              primary_actions: Array(test.recommendations_count).fill('Sample recommendation'),
              secondary_actions: [],
              timeline: 'immediate',
              expected_impact: 'high'
            },
            risk_factors: Array(test.risk_factors_count).fill('Sample risk factor'),
            opportunities: Array(test.opportunities_count).fill('Sample opportunity'),
            pricing_analysis: {
              current_price: test.vehicle.price,
              price_competitiveness_score: 75,
              pricing_insights: ['Sample pricing insight']
            },
            market_positioning: {
              market_position: 'Competitive',
              competitive_strengths: ['Sample strength'],
              competitive_weaknesses: ['Sample weakness'],
              market_dynamics: ['Sample market dynamic']
            }
          }
        }))

        setVehicleInsights(insights)
      }

      toast({
        title: "Batch Insights Generated",
        description: `Generated insights for ${result.test_results?.length || 0} vehicles`,
      })

    } catch (error) {
      toast({
        title: "Batch Generation Failed",
        description: error.message,
        variant: "destructive",
      })
    } finally {
      setGeneratingInsights(false)
    }
  }

  const getRiskBadgeVariant = (riskCount) => {
    if (riskCount >= 3) return 'destructive'
    if (riskCount >= 2) return 'secondary'
    return 'outline'
  }

  const getOpportunityBadgeVariant = (oppCount) => {
    if (oppCount >= 3) return 'default'
    if (oppCount >= 2) return 'secondary'
    return 'outline'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading insights...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">AI Insights</h1>
          <p className="text-muted-foreground">
            AI-powered pricing recommendations and market analysis
          </p>
        </div>
        <div className="flex space-x-2">
          <Button onClick={generateBatchInsights} variant="outline" disabled={generatingInsights}>
            <Zap className="w-4 h-4 mr-2" />
            Generate Batch Insights
          </Button>
          <Button onClick={loadInsightsData} variant="outline">
            Refresh Data
          </Button>
        </div>
      </div>

      <Tabs defaultValue="market" className="space-y-4">
        <TabsList>
          <TabsTrigger value="market">Market Insights</TabsTrigger>
          <TabsTrigger value="vehicle">Vehicle Insights</TabsTrigger>
          <TabsTrigger value="generate">Generate New</TabsTrigger>
        </TabsList>

        <TabsContent value="market" className="space-y-4">
          {marketInsights ? (
            <div className="grid gap-4 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Brain className="w-5 h-5" />
                    <span>Market Overview</span>
                  </CardTitle>
                  <CardDescription>
                    AI analysis of current market conditions
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm leading-relaxed">
                    {marketInsights.market_overview}
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <TrendingUp className="w-5 h-5" />
                    <span>Pricing Trends</span>
                  </CardTitle>
                  <CardDescription>
                    Market pricing dynamics and sentiment
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Trend Direction</span>
                      <Badge variant="outline">
                        {marketInsights.pricing_trends?.trend_direction || 'Unknown'}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Price Volatility</span>
                      <Badge variant="secondary">
                        {marketInsights.pricing_trends?.price_volatility || 'Unknown'}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Market Sentiment</span>
                      <Badge variant="outline">
                        {marketInsights.pricing_trends?.market_sentiment || 'Unknown'}
                      </Badge>
                    </div>
                  </div>
                  
                  {marketInsights.pricing_trends?.key_insights && (
                    <div className="mt-4">
                      <h4 className="text-sm font-medium mb-2">Key Insights</h4>
                      <ul className="text-sm space-y-1">
                        {marketInsights.pricing_trends.key_insights.map((insight, index) => (
                          <li key={index} className="flex items-start space-x-2">
                            <Lightbulb className="w-3 h-3 mt-0.5 text-yellow-500 flex-shrink-0" />
                            <span>{insight}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <CheckCircle className="w-5 h-5" />
                    <span>Inventory Health</span>
                  </CardTitle>
                  <CardDescription>
                    Overall inventory performance assessment
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Health Status</span>
                      <Badge variant={marketInsights.inventory_analysis?.inventory_health === 'excellent' ? 'default' : 'secondary'}>
                        {marketInsights.inventory_analysis?.inventory_health || 'Unknown'}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Well Positioned</span>
                      <Badge variant="outline">
                        {marketInsights.inventory_analysis?.well_positioned || 0}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Needs Attention</span>
                      <Badge variant="destructive">
                        {marketInsights.inventory_analysis?.attention_required || 0}
                      </Badge>
                    </div>
                  </div>

                  {marketInsights.inventory_analysis?.key_findings && (
                    <div className="mt-4">
                      <h4 className="text-sm font-medium mb-2">Key Findings</h4>
                      <ul className="text-sm space-y-1">
                        {marketInsights.inventory_analysis.key_findings.map((finding, index) => (
                          <li key={index} className="flex items-start space-x-2">
                            <AlertTriangle className="w-3 h-3 mt-0.5 text-orange-500 flex-shrink-0" />
                            <span>{finding}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Lightbulb className="w-5 h-5" />
                    <span>Strategic Recommendations</span>
                  </CardTitle>
                  <CardDescription>
                    AI-powered strategic guidance
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {marketInsights.strategic_recommendations && (
                    <ul className="space-y-2">
                      {marketInsights.strategic_recommendations.map((recommendation, index) => (
                        <li key={index} className="flex items-start space-x-2">
                          <CheckCircle className="w-4 h-4 mt-0.5 text-green-500 flex-shrink-0" />
                          <span className="text-sm">{recommendation}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                </CardContent>
              </Card>
            </div>
          ) : (
            <Card>
              <CardContent className="flex items-center justify-center py-8">
                <div className="text-center">
                  <Brain className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">No market insights available</p>
                  <Button onClick={loadInsightsData} className="mt-2">
                    Load Market Insights
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="vehicle" className="space-y-4">
          <div className="grid gap-4">
            {vehicleInsights.length > 0 ? (
              vehicleInsights.map((insight) => (
                <Card key={insight.vin}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg">
                        Vehicle Analysis - {insight.vin}
                      </CardTitle>
                      <div className="flex space-x-2">
                        <Badge variant="outline">
                          {insight.insights.recommendations?.primary_actions?.length || 0} Actions
                        </Badge>
                        <Badge variant={getRiskBadgeVariant(insight.insights.risk_factors?.length || 0)}>
                          {insight.insights.risk_factors?.length || 0} Risks
                        </Badge>
                        <Badge variant={getOpportunityBadgeVariant(insight.insights.opportunities?.length || 0)}>
                          {insight.insights.opportunities?.length || 0} Opportunities
                        </Badge>
                      </div>
                    </div>
                    <CardDescription>
                      AI-generated insights and recommendations
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-medium mb-2">Executive Summary</h4>
                        <p className="text-sm text-muted-foreground leading-relaxed">
                          {insight.insights.executive_summary}
                        </p>
                      </div>

                      <div className="grid gap-4 md:grid-cols-2">
                        <div>
                          <h4 className="font-medium mb-2 text-green-700">Primary Recommendations</h4>
                          <ul className="text-sm space-y-1">
                            {insight.insights.recommendations?.primary_actions?.slice(0, 3).map((action, index) => (
                              <li key={index} className="flex items-start space-x-2">
                                <CheckCircle className="w-3 h-3 mt-0.5 text-green-500 flex-shrink-0" />
                                <span>{action}</span>
                              </li>
                            ))}
                          </ul>
                        </div>

                        <div>
                          <h4 className="font-medium mb-2 text-orange-700">Risk Factors</h4>
                          <ul className="text-sm space-y-1">
                            {insight.insights.risk_factors?.slice(0, 3).map((risk, index) => (
                              <li key={index} className="flex items-start space-x-2">
                                <AlertTriangle className="w-3 h-3 mt-0.5 text-orange-500 flex-shrink-0" />
                                <span>{risk}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>

                      <div className="flex justify-end">
                        <Dialog>
                          <DialogTrigger asChild>
                            <Button 
                              variant="outline" 
                              size="sm"
                              onClick={() => setSelectedInsight(insight)}
                            >
                              <Eye className="w-4 h-4 mr-2" />
                              View Full Analysis
                            </Button>
                          </DialogTrigger>
                          <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
                            <DialogHeader>
                              <DialogTitle>
                                Complete Vehicle Analysis - {selectedInsight?.vin}
                              </DialogTitle>
                              <DialogDescription>
                                Comprehensive AI-generated insights and recommendations
                              </DialogDescription>
                            </DialogHeader>
                            
                            {selectedInsight && (
                              <div className="space-y-6">
                                <div>
                                  <h3 className="text-lg font-semibold mb-3">Executive Summary</h3>
                                  <p className="text-sm leading-relaxed">
                                    {selectedInsight.insights.executive_summary}
                                  </p>
                                </div>

                                <div className="grid gap-6 md:grid-cols-2">
                                  <div>
                                    <h3 className="text-lg font-semibold mb-3">Pricing Analysis</h3>
                                    <div className="space-y-2 text-sm">
                                      <div className="flex justify-between">
                                        <span>Current Price:</span>
                                        <span className="font-medium">
                                          ${selectedInsight.insights.pricing_analysis?.current_price?.toLocaleString() || 'N/A'}
                                        </span>
                                      </div>
                                      <div className="flex justify-between">
                                        <span>Competitiveness Score:</span>
                                        <span className="font-medium">
                                          {selectedInsight.insights.pricing_analysis?.price_competitiveness_score || 'N/A'}
                                        </span>
                                      </div>
                                    </div>
                                    {selectedInsight.insights.pricing_analysis?.pricing_insights && (
                                      <div className="mt-3">
                                        <h4 className="font-medium mb-2">Pricing Insights</h4>
                                        <ul className="text-sm space-y-1">
                                          {selectedInsight.insights.pricing_analysis.pricing_insights.map((insight, index) => (
                                            <li key={index} className="flex items-start space-x-2">
                                              <Lightbulb className="w-3 h-3 mt-0.5 text-yellow-500 flex-shrink-0" />
                                              <span>{insight}</span>
                                            </li>
                                          ))}
                                        </ul>
                                      </div>
                                    )}
                                  </div>

                                  <div>
                                    <h3 className="text-lg font-semibold mb-3">Market Position</h3>
                                    <div className="space-y-3">
                                      <div>
                                        <span className="text-sm font-medium">Position: </span>
                                        <Badge variant="outline">
                                          {selectedInsight.insights.market_positioning?.market_position || 'Unknown'}
                                        </Badge>
                                      </div>
                                      
                                      {selectedInsight.insights.market_positioning?.competitive_strengths?.length > 0 && (
                                        <div>
                                          <h4 className="font-medium mb-2 text-green-700">Strengths</h4>
                                          <ul className="text-sm space-y-1">
                                            {selectedInsight.insights.market_positioning.competitive_strengths.map((strength, index) => (
                                              <li key={index} className="flex items-start space-x-2">
                                                <CheckCircle className="w-3 h-3 mt-0.5 text-green-500 flex-shrink-0" />
                                                <span>{strength}</span>
                                              </li>
                                            ))}
                                          </ul>
                                        </div>
                                      )}

                                      {selectedInsight.insights.market_positioning?.competitive_weaknesses?.length > 0 && (
                                        <div>
                                          <h4 className="font-medium mb-2 text-red-700">Weaknesses</h4>
                                          <ul className="text-sm space-y-1">
                                            {selectedInsight.insights.market_positioning.competitive_weaknesses.map((weakness, index) => (
                                              <li key={index} className="flex items-start space-x-2">
                                                <AlertTriangle className="w-3 h-3 mt-0.5 text-red-500 flex-shrink-0" />
                                                <span>{weakness}</span>
                                              </li>
                                            ))}
                                          </ul>
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                </div>

                                <div className="grid gap-6 md:grid-cols-2">
                                  <div>
                                    <h3 className="text-lg font-semibold mb-3">Recommendations</h3>
                                    <div className="space-y-3">
                                      <div>
                                        <h4 className="font-medium mb-2">Primary Actions</h4>
                                        <ul className="text-sm space-y-1">
                                          {selectedInsight.insights.recommendations?.primary_actions?.map((action, index) => (
                                            <li key={index} className="flex items-start space-x-2">
                                              <CheckCircle className="w-3 h-3 mt-0.5 text-green-500 flex-shrink-0" />
                                              <span>{action}</span>
                                            </li>
                                          ))}
                                        </ul>
                                      </div>
                                      
                                      {selectedInsight.insights.recommendations?.secondary_actions?.length > 0 && (
                                        <div>
                                          <h4 className="font-medium mb-2">Secondary Actions</h4>
                                          <ul className="text-sm space-y-1">
                                            {selectedInsight.insights.recommendations.secondary_actions.map((action, index) => (
                                              <li key={index} className="flex items-start space-x-2">
                                                <Lightbulb className="w-3 h-3 mt-0.5 text-yellow-500 flex-shrink-0" />
                                                <span>{action}</span>
                                              </li>
                                            ))}
                                          </ul>
                                        </div>
                                      )}
                                    </div>
                                  </div>

                                  <div>
                                    <h3 className="text-lg font-semibold mb-3">Opportunities</h3>
                                    <ul className="text-sm space-y-1">
                                      {selectedInsight.insights.opportunities?.map((opportunity, index) => (
                                        <li key={index} className="flex items-start space-x-2">
                                          <TrendingUp className="w-3 h-3 mt-0.5 text-blue-500 flex-shrink-0" />
                                          <span>{opportunity}</span>
                                        </li>
                                      ))}
                                    </ul>
                                  </div>
                                </div>
                              </div>
                            )}
                          </DialogContent>
                        </Dialog>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            ) : (
              <Card>
                <CardContent className="flex items-center justify-center py-8">
                  <div className="text-center">
                    <Brain className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                    <p className="text-muted-foreground mb-4">No vehicle insights generated yet</p>
                    <Button onClick={generateBatchInsights} disabled={generatingInsights}>
                      <Zap className="w-4 h-4 mr-2" />
                      Generate Sample Insights
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        <TabsContent value="generate" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Generate Vehicle Insights</CardTitle>
                <CardDescription>
                  Generate AI insights for a specific vehicle by VIN
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">Vehicle VIN</label>
                  <Input
                    placeholder="Enter VIN (e.g., 5NPEL4JA2LH042897)"
                    value={selectedVin}
                    onChange={(e) => setSelectedVin(e.target.value.toUpperCase())}
                  />
                </div>
                
                <Button 
                  onClick={() => generateVehicleInsight(selectedVin)}
                  disabled={generatingInsights || !selectedVin}
                  className="w-full"
                >
                  <Brain className="w-4 h-4 mr-2" />
                  {generatingInsights ? 'Generating...' : 'Generate Insights'}
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Batch Generation</CardTitle>
                <CardDescription>
                  Generate insights for multiple vehicles at once
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-muted-foreground">
                  Generate AI insights for a sample of vehicles to get started with analysis.
                </p>
                
                <Button 
                  onClick={generateBatchInsights}
                  disabled={generatingInsights}
                  className="w-full"
                >
                  <Zap className="w-4 h-4 mr-2" />
                  {generatingInsights ? 'Generating...' : 'Generate Batch Insights'}
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}

