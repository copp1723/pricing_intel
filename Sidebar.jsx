import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  BarChart3, 
  Car, 
  TrendingUp, 
  Brain, 
  Settings, 
  Menu, 
  X,
  Database,
  Activity
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'

const navigation = [
  { name: 'Dashboard', href: '/', icon: BarChart3 },
  { name: 'Inventory', href: '/inventory', icon: Car },
  { name: 'Analytics', href: '/analytics', icon: TrendingUp },
  { name: 'AI Insights', href: '/insights', icon: Brain },
  { name: 'Settings', href: '/settings', icon: Settings },
]

export function Sidebar({ open, onToggle, systemStats }) {
  const location = useLocation()

  return (
    <>
      {/* Mobile overlay */}
      {open && (
        <div 
          className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 lg:hidden"
          onClick={onToggle}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed left-0 top-0 z-50 h-full bg-sidebar border-r border-sidebar-border
        transition-all duration-300 ease-in-out
        ${open ? 'w-64' : 'w-16'}
        ${open ? 'translate-x-0' : '-translate-x-48 lg:translate-x-0'}
      `}>
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-sidebar-border">
          {open && (
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <Activity className="w-4 h-4 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-sm font-semibold text-sidebar-foreground">
                  Pricing Intelligence
                </h1>
                <p className="text-xs text-sidebar-foreground/60">
                  Platform
                </p>
              </div>
            </div>
          )}
          
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggle}
            className="text-sidebar-foreground hover:bg-sidebar-accent"
          >
            {open ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
          </Button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2">
          {navigation.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.href
            
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`
                  flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors
                  ${isActive 
                    ? 'bg-sidebar-accent text-sidebar-accent-foreground' 
                    : 'text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground'
                  }
                  ${!open && 'justify-center'}
                `}
              >
                <Icon className="w-5 h-5 flex-shrink-0" />
                {open && (
                  <span className="text-sm font-medium">{item.name}</span>
                )}
              </Link>
            )
          })}
        </nav>

        {/* System Stats */}
        {open && systemStats && (
          <div className="p-4 border-t border-sidebar-border">
            <Card className="bg-sidebar-accent/50">
              <CardContent className="p-3">
                <div className="flex items-center space-x-2 mb-2">
                  <Database className="w-4 h-4 text-sidebar-foreground" />
                  <span className="text-sm font-medium text-sidebar-foreground">
                    System Status
                  </span>
                </div>
                
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-sidebar-foreground/60">Total Vehicles</span>
                    <Badge variant="secondary" className="text-xs">
                      {systemStats.total_vehicles || 0}
                    </Badge>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-sidebar-foreground/60">Makes</span>
                    <Badge variant="secondary" className="text-xs">
                      {systemStats.unique_makes || 0}
                    </Badge>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-sidebar-foreground/60">Models</span>
                    <Badge variant="secondary" className="text-xs">
                      {systemStats.unique_models || 0}
                    </Badge>
                  </div>

                  {systemStats.price_range && (
                    <div className="pt-2 border-t border-sidebar-border/50">
                      <div className="flex justify-between">
                        <span className="text-sidebar-foreground/60">Avg Price</span>
                        <span className="text-sidebar-foreground text-xs font-medium">
                          ${Math.round(systemStats.price_range.avg || 0).toLocaleString()}
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Collapsed stats indicator */}
        {!open && systemStats && (
          <div className="p-2 border-t border-sidebar-border">
            <div className="flex flex-col items-center space-y-1">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-xs text-sidebar-foreground/60">
                {systemStats.total_vehicles || 0}
              </span>
            </div>
          </div>
        )}
      </div>
    </>
  )
}

