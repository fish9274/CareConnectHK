import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { 
  Search, 
  MapPin, 
  Star, 
  Clock, 
  DollarSign,
  CheckCircle,
  Filter,
  Loader2
} from 'lucide-react'

const ProviderSearch = () => {
  const [providers, setProviders] = useState([])
  const [loading, setLoading] = useState(false)
  const [searchFilters, setSearchFilters] = useState({
    city: '',
    service_type: '',
    min_rating: '',
    verified_only: false
  })

  const serviceTypes = [
    { value: 'home_care', label: 'In-Home Care' },
    { value: 'medical_services', label: 'Medical Services' },
    { value: 'adult_day_care', label: 'Adult Day Care' },
    { value: 'pharmacy_services', label: 'Pharmacy Services' },
    { value: 'companionship', label: 'Companionship' },
    { value: 'transportation', label: 'Transportation' }
  ]

  const fetchProviders = async () => {
    setLoading(true)
    try {
      const queryParams = new URLSearchParams()
      
      if (searchFilters.city) queryParams.append('city', searchFilters.city)
      if (searchFilters.service_type) queryParams.append('service_type', searchFilters.service_type)
      if (searchFilters.min_rating) queryParams.append('min_rating', searchFilters.min_rating)
      if (searchFilters.verified_only) queryParams.append('verified_only', 'true')
      
      const response = await fetch(`/api/providers?${queryParams}`)
      const data = await response.json()
      
      if (response.ok) {
        setProviders(data.providers)
      } else {
        console.error('Error fetching providers:', data.error)
      }
    } catch (error) {
      console.error('Error fetching providers:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchProviders()
  }, [])

  const handleSearch = () => {
    fetchProviders()
  }

  const handleFilterChange = (key, value) => {
    setSearchFilters(prev => ({
      ...prev,
      [key]: value
    }))
  }

  const formatPrice = (provider) => {
    if (provider.hourly_rate) {
      return `$${provider.hourly_rate}/hour`
    } else if (provider.daily_rate) {
      return `$${provider.daily_rate}/day`
    }
    return 'Contact for pricing'
  }

  const getAvailabilityStatus = () => {
    // This would normally check real availability
    const statuses = ['Available Today', 'Available Tomorrow', 'Available This Week']
    return statuses[Math.floor(Math.random() * statuses.length)]
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Find Care Providers</h1>
        <p className="text-gray-600 mb-6">
          Search our verified network of healthcare providers and caregivers
        </p>

        {/* Search Filters */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Filter className="w-5 h-5" />
              Search Filters
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Location
                </label>
                <Input
                  placeholder="Enter city..."
                  value={searchFilters.city}
                  onChange={(e) => handleFilterChange('city', e.target.value)}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Service Type
                </label>
                <Select 
                  value={searchFilters.service_type} 
                  onValueChange={(value) => handleFilterChange('service_type', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select service..." />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">All Services</SelectItem>
                    {serviceTypes.map((service) => (
                      <SelectItem key={service.value} value={service.value}>
                        {service.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Minimum Rating
                </label>
                <Select 
                  value={searchFilters.min_rating} 
                  onValueChange={(value) => handleFilterChange('min_rating', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Any rating..." />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">Any Rating</SelectItem>
                    <SelectItem value="4.5">4.5+ Stars</SelectItem>
                    <SelectItem value="4.0">4.0+ Stars</SelectItem>
                    <SelectItem value="3.5">3.5+ Stars</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="flex items-end">
                <Button onClick={handleSearch} className="w-full" disabled={loading}>
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Searching...
                    </>
                  ) : (
                    <>
                      <Search className="w-4 h-4 mr-2" />
                      Search
                    </>
                  )}
                </Button>
              </div>
            </div>
            
            <div className="mt-4">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={searchFilters.verified_only}
                  onChange={(e) => handleFilterChange('verified_only', e.target.checked)}
                  className="rounded border-gray-300"
                />
                <span className="text-sm text-gray-700">Show only verified providers</span>
              </label>
            </div>
          </CardContent>
        </Card>

        {/* Results */}
        <div className="mb-4">
          <p className="text-gray-600">
            {loading ? 'Searching...' : `Found ${providers.length} providers`}
          </p>
        </div>

        {/* Provider Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {providers.map((provider) => (
            <Card key={provider.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-lg flex items-center gap-2">
                      {provider.business_name || `${provider.user.first_name} ${provider.user.last_name}`}
                      {provider.is_verified && (
                        <CheckCircle className="w-5 h-5 text-green-500" />
                      )}
                    </CardTitle>
                    <CardDescription className="text-blue-600 font-medium capitalize">
                      {provider.provider_type.replace('_', ' ')}
                    </CardDescription>
                  </div>
                  <Badge variant="secondary" className="text-green-600 bg-green-100">
                    {getAvailabilityStatus()}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <Star className="w-4 h-4 text-yellow-400 fill-current" />
                    <span className="font-medium">{provider.rating}</span>
                    <span className="text-gray-500">({provider.total_reviews} reviews)</span>
                  </div>
                  
                  <div className="flex items-center gap-2 text-gray-600">
                    <MapPin className="w-4 h-4" />
                    <span>{provider.city}, {provider.state}</span>
                  </div>
                  
                  <div className="flex items-center gap-2 text-gray-600">
                    <DollarSign className="w-4 h-4" />
                    <span className="font-medium text-gray-900">{formatPrice(provider)}</span>
                  </div>
                  
                  {provider.specialties && (
                    <div>
                      <p className="text-sm font-medium text-gray-700 mb-1">Specialties:</p>
                      <div className="flex flex-wrap gap-1">
                        {provider.specialties.split(', ').slice(0, 3).map((specialty, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {specialty}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {provider.services && provider.services.length > 0 && (
                    <div>
                      <p className="text-sm font-medium text-gray-700 mb-1">Services:</p>
                      <div className="flex flex-wrap gap-1">
                        {provider.services.slice(0, 2).map((service) => (
                          <Badge key={service.id} variant="outline" className="text-xs">
                            {service.name}
                          </Badge>
                        ))}
                        {provider.services.length > 2 && (
                          <Badge variant="outline" className="text-xs">
                            +{provider.services.length - 2} more
                          </Badge>
                        )}
                      </div>
                    </div>
                  )}
                  
                  <div className="flex gap-2 pt-2">
                    <Button className="flex-1" size="sm">
                      Book Now
                    </Button>
                    <Button variant="outline" size="sm">
                      View Profile
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {providers.length === 0 && !loading && (
          <div className="text-center py-12">
            <div className="text-gray-400 mb-4">
              <Search className="w-16 h-16 mx-auto" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No providers found</h3>
            <p className="text-gray-600">
              Try adjusting your search filters to find more providers in your area.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default ProviderSearch
