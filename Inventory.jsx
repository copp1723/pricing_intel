import { useState, useEffect } from 'react'
import { Search, Filter, Eye, Calculator, Target, ExternalLink } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { useToast } from '@/hooks/use-toast'

export function Inventory({ apiService }) {
  const [vehicles, setVehicles] = useState([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    search: '',
    make: '',
    condition: '',
    page: 1,
    per_page: 20
  })
  const [pagination, setPagination] = useState(null)
  const [selectedVehicle, setSelectedVehicle] = useState(null)
  const [vehicleDetails, setVehicleDetails] = useState(null)
  const [loadingDetails, setLoadingDetails] = useState(false)
  const { toast } = useToast()

  useEffect(() => {
    loadVehicles()
  }, [filters])

  const loadVehicles = async () => {
    try {
      setLoading(true)
      const params = {}
      
      if (filters.search) {
        // Search in make or model
        params.make = filters.search
      }
      if (filters.make) params.make = filters.make
      if (filters.condition) params.condition = filters.condition
      params.page = filters.page
      params.per_page = filters.per_page

      const response = await apiService.getVehicles(params)
      setVehicles(response.vehicles || [])
      setPagination(response.pagination)
    } catch (error) {
      console.error('Failed to load vehicles:', error)
      toast({
        title: "Error",
        description: "Failed to load vehicle inventory",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const loadVehicleDetails = async (vin) => {
    try {
      setLoadingDetails(true)
      const vehicle = await apiService.getVehicle(vin)
      setVehicleDetails(vehicle)
    } catch (error) {
      console.error('Failed to load vehicle details:', error)
      toast({
        title: "Error",
        description: "Failed to load vehicle details",
        variant: "destructive",
      })
    } finally {
      setLoadingDetails(false)
    }
  }

  const calculateScore = async (vin) => {
    try {
      toast({
        title: "Calculating Score",
        description: "Analyzing vehicle competitiveness...",
      })

      await apiService.calculateScore(vin)
      
      toast({
        title: "Score Calculated",
        description: "Pricing score has been calculated successfully",
      })
      
      // Refresh vehicle details if open
      if (selectedVehicle?.vin === vin) {
        loadVehicleDetails(vin)
      }
    } catch (error) {
      toast({
        title: "Calculation Failed",
        description: error.message,
        variant: "destructive",
      })
    }
  }

  const findMatches = async (vin) => {
    try {
      toast({
        title: "Finding Matches",
        description: "Searching for comparable vehicles...",
      })

      const result = await apiService.findMatches(vin, {
        min_similarity: 0.3,
        max_matches: 10,
        exclude_same_dealer: false
      })
      
      toast({
        title: "Matches Found",
        description: `Found ${result.summary?.matches_found || 0} comparable vehicles`,
      })
      
      // Refresh vehicle details if open
      if (selectedVehicle?.vin === vin) {
        loadVehicleDetails(vin)
      }
    } catch (error) {
      toast({
        title: "Search Failed",
        description: error.message,
        variant: "destructive",
      })
    }
  }

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
      page: 1 // Reset to first page when filtering
    }))
  }

  const handlePageChange = (newPage) => {
    setFilters(prev => ({
      ...prev,
      page: newPage
    }))
  }

  const getConditionBadge = (condition) => {
    const variants = {
      'New': 'default',
      'Certified': 'secondary',
      'Used': 'outline'
    }
    return <Badge variant={variants[condition] || 'outline'}>{condition}</Badge>
  }

  const formatPrice = (price) => {
    return price ? `$${price.toLocaleString()}` : 'N/A'
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Vehicle Inventory</h1>
          <p className="text-muted-foreground">
            Manage and analyze your vehicle inventory
          </p>
        </div>
        <Button onClick={loadVehicles} variant="outline">
          Refresh Inventory
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
          <CardDescription>
            Filter and search your vehicle inventory
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-4">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search make or model..."
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                className="pl-9"
              />
            </div>
            
            <Select value={filters.make} onValueChange={(value) => handleFilterChange('make', value)}>
              <SelectTrigger>
                <SelectValue placeholder="Select make" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Makes</SelectItem>
                <SelectItem value="HYUNDAI">Hyundai</SelectItem>
                <SelectItem value="FORD">Ford</SelectItem>
                <SelectItem value="CHEVROLET">Chevrolet</SelectItem>
                <SelectItem value="NISSAN">Nissan</SelectItem>
                <SelectItem value="TOYOTA">Toyota</SelectItem>
              </SelectContent>
            </Select>

            <Select value={filters.condition} onValueChange={(value) => handleFilterChange('condition', value)}>
              <SelectTrigger>
                <SelectValue placeholder="Select condition" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Conditions</SelectItem>
                <SelectItem value="New">New</SelectItem>
                <SelectItem value="Certified">Certified</SelectItem>
                <SelectItem value="Used">Used</SelectItem>
              </SelectContent>
            </Select>

            <Button variant="outline" onClick={() => setFilters({
              search: '', make: '', condition: '', page: 1, per_page: 20
            })}>
              <Filter className="w-4 h-4 mr-2" />
              Clear Filters
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Vehicle Table */}
      <Card>
        <CardHeader>
          <CardTitle>Vehicles</CardTitle>
          <CardDescription>
            {pagination && `Showing ${((pagination.page - 1) * pagination.per_page) + 1}-${Math.min(pagination.page * pagination.per_page, pagination.total)} of ${pagination.total} vehicles`}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Vehicle</TableHead>
                    <TableHead>Condition</TableHead>
                    <TableHead>Mileage</TableHead>
                    <TableHead>Price</TableHead>
                    <TableHead>Stock #</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {vehicles.map((vehicle) => (
                    <TableRow key={vehicle.id}>
                      <TableCell>
                        <div>
                          <div className="font-medium">
                            {vehicle.year} {vehicle.make} {vehicle.model}
                          </div>
                          {vehicle.trim && (
                            <div className="text-sm text-muted-foreground">
                              {vehicle.trim}
                            </div>
                          )}
                          <div className="text-xs text-muted-foreground">
                            VIN: {vehicle.vin}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        {getConditionBadge(vehicle.condition)}
                      </TableCell>
                      <TableCell>
                        {vehicle.mileage ? vehicle.mileage.toLocaleString() : 'N/A'}
                      </TableCell>
                      <TableCell className="font-medium">
                        {formatPrice(vehicle.price)}
                      </TableCell>
                      <TableCell>
                        {vehicle.stock_number || 'N/A'}
                      </TableCell>
                      <TableCell>
                        <div className="flex space-x-1">
                          <Dialog>
                            <DialogTrigger asChild>
                              <Button 
                                variant="outline" 
                                size="sm"
                                onClick={() => {
                                  setSelectedVehicle(vehicle)
                                  loadVehicleDetails(vehicle.vin)
                                }}
                              >
                                <Eye className="w-4 h-4" />
                              </Button>
                            </DialogTrigger>
                            <DialogContent className="max-w-2xl">
                              <DialogHeader>
                                <DialogTitle>
                                  {selectedVehicle?.year} {selectedVehicle?.make} {selectedVehicle?.model}
                                </DialogTitle>
                                <DialogDescription>
                                  Vehicle details and analysis
                                </DialogDescription>
                              </DialogHeader>
                              
                              {loadingDetails ? (
                                <div className="flex items-center justify-center py-8">
                                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                                </div>
                              ) : vehicleDetails && (
                                <div className="space-y-4">
                                  <div className="grid grid-cols-2 gap-4">
                                    <div>
                                      <h4 className="font-medium mb-2">Basic Information</h4>
                                      <div className="space-y-1 text-sm">
                                        <div>VIN: {vehicleDetails.vin}</div>
                                        <div>Year: {vehicleDetails.year}</div>
                                        <div>Make: {vehicleDetails.make}</div>
                                        <div>Model: {vehicleDetails.model}</div>
                                        <div>Trim: {vehicleDetails.trim || 'N/A'}</div>
                                        <div>Condition: {vehicleDetails.condition}</div>
                                        <div>Mileage: {vehicleDetails.mileage?.toLocaleString() || 'N/A'}</div>
                                      </div>
                                    </div>
                                    
                                    <div>
                                      <h4 className="font-medium mb-2">Pricing</h4>
                                      <div className="space-y-1 text-sm">
                                        <div>Price: {formatPrice(vehicleDetails.price)}</div>
                                        <div>Alt Price: {formatPrice(vehicleDetails.price_alt)}</div>
                                        <div>Discount: {vehicleDetails.discount ? `$${vehicleDetails.discount}` : 'None'}</div>
                                        <div>Stock #: {vehicleDetails.stock_number || 'N/A'}</div>
                                        <div>Color: {vehicleDetails.color || 'N/A'}</div>
                                      </div>
                                    </div>
                                  </div>

                                  {vehicleDetails.vin_decoded && (
                                    <div>
                                      <h4 className="font-medium mb-2">VIN Decoded</h4>
                                      <div className="grid grid-cols-2 gap-2 text-sm">
                                        <div>Body Class: {vehicleDetails.vin_decoded.body_class}</div>
                                        <div>Doors: {vehicleDetails.vin_decoded.doors}</div>
                                        <div>Fuel Type: {vehicleDetails.vin_decoded.fuel_type}</div>
                                        <div>Engine: {vehicleDetails.vin_decoded.engine}</div>
                                      </div>
                                    </div>
                                  )}

                                  {vehicleDetails.listing_url && (
                                    <div>
                                      <Button variant="outline" size="sm" asChild>
                                        <a href={vehicleDetails.listing_url} target="_blank" rel="noopener noreferrer">
                                          <ExternalLink className="w-4 h-4 mr-2" />
                                          View Listing
                                        </a>
                                      </Button>
                                    </div>
                                  )}
                                </div>
                              )}
                            </DialogContent>
                          </Dialog>

                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => calculateScore(vehicle.vin)}
                          >
                            <Calculator className="w-4 h-4" />
                          </Button>

                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => findMatches(vehicle.vin)}
                          >
                            <Target className="w-4 h-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              {/* Pagination */}
              {pagination && pagination.pages > 1 && (
                <div className="flex items-center justify-between mt-4">
                  <div className="text-sm text-muted-foreground">
                    Page {pagination.page} of {pagination.pages}
                  </div>
                  <div className="flex space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handlePageChange(pagination.page - 1)}
                      disabled={pagination.page <= 1}
                    >
                      Previous
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handlePageChange(pagination.page + 1)}
                      disabled={pagination.page >= pagination.pages}
                    >
                      Next
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

