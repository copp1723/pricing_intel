import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Sidebar } from './components/Sidebar'
import { Dashboard } from './pages/Dashboard'
import { Inventory } from './pages/Inventory'
import { Analytics } from './pages/Analytics'
import { Insights } from './pages/Insights'
import { Settings } from './pages/Settings'
import { Toaster } from '@/components/ui/toaster'
import './App.css'

// API Configuration
const API_BASE_URL = 'http://localhost:5001/api'

// API Service
export const apiService = {
  async get(endpoint) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return response.json()
  },

  async post(endpoint, data) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return response.json()
  },

  // Specific API methods
  getStats: () => apiService.get('/stats'),
  getVehicles: (params = {}) => {
    const queryString = new URLSearchParams(params).toString()
    return apiService.get(`/vehicles${queryString ? `?${queryString}` : ''}`)
  },
  getVehicle: (vin) => apiService.get(`/vehicles/${vin}`),
  getAnalytics: () => apiService.get('/analytics'),
  getMatchingStats: () => apiService.get('/matching-stats'),
  getVehicleInsights: (vin) => apiService.get(`/vehicle-insights/${vin}`),
  getMarketInsights: () => apiService.get('/market-insights'),
  calculateScore: (vin) => apiService.post(`/calculate-score/${vin}`, {}),
  findMatches: (vin, options = {}) => apiService.post(`/find-matches/${vin}`, options),
  testScoring: (options = {}) => apiService.post('/test-scoring', options),
  testInsights: (options = {}) => apiService.post('/test-insights', options),
}

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [systemStats, setSystemStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Load initial system stats
    const loadStats = async () => {
      try {
        const stats = await apiService.getStats()
        setSystemStats(stats)
      } catch (error) {
        console.error('Failed to load system stats:', error)
      } finally {
        setLoading(false)
      }
    }

    loadStats()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading Pricing Intelligence Platform...</p>
        </div>
      </div>
    )
  }

  return (
    <Router>
      <div className="flex h-screen bg-background">
        <Sidebar 
          open={sidebarOpen} 
          onToggle={() => setSidebarOpen(!sidebarOpen)}
          systemStats={systemStats}
        />
        
        <main className={`flex-1 overflow-hidden transition-all duration-300 ${
          sidebarOpen ? 'ml-64' : 'ml-16'
        }`}>
          <Routes>
            <Route 
              path="/" 
              element={<Dashboard systemStats={systemStats} apiService={apiService} />} 
            />
            <Route 
              path="/inventory" 
              element={<Inventory apiService={apiService} />} 
            />
            <Route 
              path="/analytics" 
              element={<Analytics apiService={apiService} />} 
            />
            <Route 
              path="/insights" 
              element={<Insights apiService={apiService} />} 
            />
            <Route 
              path="/settings" 
              element={<Settings apiService={apiService} />} 
            />
          </Routes>
        </main>
        
        <Toaster />
      </div>
    </Router>
  )
}

export default App

