import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { 
  Heart, 
  Shield, 
  Clock, 
  MapPin, 
  Star, 
  Phone, 
  Calendar, 
  Users, 
  Stethoscope, 
  Home, 
  Pill,
  Search,
  Menu,
  X,
  ChevronRight,
  CheckCircle,
  AlertCircle,
  User,
  ArrowLeft
} from 'lucide-react'
import ProviderSearch from './components/ProviderSearch.jsx'
import BookingForm from './components/BookingForm.jsx'
import './App.css'

function App() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [currentView, setCurrentView] = useState('home') // 'home', 'search', 'booking'
  const [selectedProvider, setSelectedProvider] = useState(null)
  const [selectedService, setSelectedService] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')

  // Sample data for providers (for the home page)
  const featuredProviders = [
    {
      id: 1,
      name: "Sarah Johnson, RN",
      type: "Home Care Nurse",
      rating: 4.9,
      reviews: 127,
      location: "Downtown Area",
      price: "$45/hour",
      verified: true,
      availability: "Available Today",
      specialties: ["Medication Management", "Wound Care", "Companionship"]
    },
    {
      id: 2,
      name: "Sunshine Senior Center",
      type: "Adult Day Care",
      rating: 4.8,
      reviews: 89,
      location: "Westside",
      price: "$65/day",
      verified: true,
      availability: "Open 7am-6pm",
      specialties: ["Social Activities", "Meals", "Transportation"]
    },
    {
      id: 3,
      name: "Michael Chen, CNA",
      type: "Personal Care Assistant",
      rating: 4.7,
      reviews: 156,
      location: "Northside",
      price: "$35/hour",
      verified: true,
      availability: "Available Tomorrow",
      specialties: ["Personal Hygiene", "Mobility Assistance", "Light Housekeeping"]
    }
  ]

  const services = [
    {
      icon: <Home className="w-8 h-8" />,
      title: "In-Home Care",
      description: "Professional caregivers providing personalized care in the comfort of home"
    },
    {
      icon: <Stethoscope className="w-8 h-8" />,
      title: "Medical Services",
      description: "Qualified nurses and healthcare professionals for medical needs"
    },
    {
      icon: <Users className="w-8 h-8" />,
      title: "Adult Day Care",
      description: "Safe, engaging environments for seniors during daytime hours"
    },
    {
      icon: <Pill className="w-8 h-8" />,
      title: "Pharmacy Services",
      description: "Medication delivery and management from verified pharmacies"
    }
  ]

  const features = [
    {
      icon: <Shield className="w-6 h-6" />,
      title: "Verified Providers",
      description: "All caregivers undergo thorough background checks and verification"
    },
    {
      icon: <Clock className="w-6 h-6" />,
      title: "24/7 Support",
      description: "Round-the-clock assistance and emergency response available"
    },
    {
      icon: <Heart className="w-6 h-6" />,
      title: "Personalized Care",
      description: "Customized care plans tailored to individual needs and preferences"
    }
  ]

  const handleBookNow = (provider) => {
    // For demo purposes, we'll use the first service of the provider
    const service = {
      id: 1,
      name: "In-Home Care Service",
      price: 45,
      duration_minutes: 120
    }
    setSelectedProvider(provider)
    setSelectedService(service)
    setCurrentView('booking')
  }

  const handleBookingComplete = (bookingData) => {
    console.log('Booking completed:', bookingData)
    setCurrentView('home')
    setSelectedProvider(null)
    setSelectedService(null)
  }

  const renderNavigation = () => (
    <nav className="bg-white shadow-lg sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0 flex items-center cursor-pointer" onClick={() => setCurrentView('home')}>
              <Heart className="w-8 h-8 text-blue-600 mr-2" />
              <span className="text-2xl font-bold text-gray-900">CareConnect</span>
            </div>
          </div>
          
          {/* Desktop Navigation */}
          <div className="hidden md:block">
            <div className="ml-10 flex items-baseline space-x-4">
              <button 
                onClick={() => setCurrentView('search')}
                className="text-gray-900 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Find Care
              </button>
              <a href="#" className="text-gray-500 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors">For Providers</a>
              <a href="#" className="text-gray-500 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors">About</a>
              <a href="#" className="text-gray-500 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors">Contact</a>
            </div>
          </div>

          <div className="hidden md:flex items-center space-x-4">
            <Button variant="outline" size="sm">Sign In</Button>
            <Button size="sm">Get Started</Button>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
              {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </Button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      {isMenuOpen && (
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-white border-t">
            <button 
              onClick={() => {setCurrentView('search'); setIsMenuOpen(false)}}
              className="text-gray-900 hover:text-blue-600 block px-3 py-2 rounded-md text-base font-medium w-full text-left"
            >
              Find Care
            </button>
            <a href="#" className="text-gray-500 hover:text-blue-600 block px-3 py-2 rounded-md text-base font-medium">For Providers</a>
            <a href="#" className="text-gray-500 hover:text-blue-600 block px-3 py-2 rounded-md text-base font-medium">About</a>
            <a href="#" className="text-gray-500 hover:text-blue-600 block px-3 py-2 rounded-md text-base font-medium">Contact</a>
            <div className="flex space-x-2 px-3 py-2">
              <Button variant="outline" size="sm" className="flex-1">Sign In</Button>
              <Button size="sm" className="flex-1">Get Started</Button>
            </div>
          </div>
        </div>
      )}
    </nav>
  )

  const renderHomePage = () => (
    <>
      {/* Hero Section */}
      <section className="relative py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
              Connecting Families with
              <span className="text-blue-600 block">Trusted Elder Care</span>
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              Find verified caregivers, book services, and manage care for your loved ones through our comprehensive platform. Peace of mind is just a click away.
            </p>
            
            {/* Search Bar */}
            <div className="max-w-2xl mx-auto mb-8">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <Input
                  type="text"
                  placeholder="Search for care services, providers, or locations..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 pr-4 py-3 text-lg"
                />
                <Button 
                  className="absolute right-2 top-1/2 transform -translate-y-1/2"
                  onClick={() => setCurrentView('search')}
                >
                  Search
                </Button>
              </div>
            </div>

            <div className="flex flex-wrap justify-center gap-4">
              <Button 
                size="lg" 
                className="bg-blue-600 hover:bg-blue-700"
                onClick={() => setCurrentView('search')}
              >
                Find Care Now
                <ChevronRight className="ml-2 w-4 h-4" />
              </Button>
              <Button variant="outline" size="lg">
                Emergency Support
                <Phone className="ml-2 w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Services Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Comprehensive Care Services
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              From in-home assistance to medical care, we connect you with the right professionals for every need.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {services.map((service, index) => (
              <Card key={index} className="text-center hover:shadow-lg transition-shadow cursor-pointer">
                <CardHeader>
                  <div className="mx-auto mb-4 p-3 bg-blue-100 rounded-full w-fit text-blue-600">
                    {service.icon}
                  </div>
                  <CardTitle className="text-xl">{service.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-gray-600">
                    {service.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Providers Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Featured Care Providers
            </h2>
            <p className="text-xl text-gray-600">
              Highly rated and verified professionals ready to help
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {featuredProviders.map((provider) => (
              <Card key={provider.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-lg flex items-center gap-2">
                        {provider.name}
                        {provider.verified && (
                          <CheckCircle className="w-5 h-5 text-green-500" />
                        )}
                      </CardTitle>
                      <CardDescription className="text-blue-600 font-medium">
                        {provider.type}
                      </CardDescription>
                    </div>
                    <Badge variant="secondary" className="text-green-600 bg-green-100">
                      {provider.availability}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      <Star className="w-4 h-4 text-yellow-400 fill-current" />
                      <span className="font-medium">{provider.rating}</span>
                      <span className="text-gray-500">({provider.reviews} reviews)</span>
                    </div>
                    
                    <div className="flex items-center gap-2 text-gray-600">
                      <MapPin className="w-4 h-4" />
                      <span>{provider.location}</span>
                    </div>
                    
                    <div className="flex items-center gap-2 text-gray-600">
                      <span className="font-medium text-gray-900">{provider.price}</span>
                    </div>
                    
                    <div className="flex flex-wrap gap-1">
                      {provider.specialties.map((specialty, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {specialty}
                        </Badge>
                      ))}
                    </div>
                    
                    <div className="flex gap-2 pt-2">
                      <Button 
                        className="flex-1" 
                        size="sm"
                        onClick={() => handleBookNow(provider)}
                      >
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
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Why Choose CareConnect?
            </h2>
            <p className="text-xl text-gray-600">
              We're committed to providing the highest quality care connections
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="text-center">
                <div className="mx-auto mb-4 p-3 bg-blue-100 rounded-full w-fit text-blue-600">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-blue-600">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Ready to Find the Perfect Care?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join thousands of families who trust CareConnect for their elder care needs
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button 
              size="lg" 
              variant="secondary" 
              className="bg-white text-blue-600 hover:bg-gray-100"
              onClick={() => setCurrentView('search')}
            >
              Get Started Today
            </Button>
            <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-blue-600">
              Schedule a Demo
            </Button>
          </div>
        </div>
      </section>
    </>
  )

  const renderFooter = () => (
    <footer className="bg-gray-900 text-white py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center mb-4">
              <Heart className="w-8 h-8 text-blue-400 mr-2" />
              <span className="text-2xl font-bold">CareConnect</span>
            </div>
            <p className="text-gray-400">
              Connecting families with trusted elder care professionals for peace of mind and quality care.
            </p>
          </div>
          
          <div>
            <h3 className="text-lg font-semibold mb-4">Services</h3>
            <ul className="space-y-2 text-gray-400">
              <li><a href="#" className="hover:text-white transition-colors">In-Home Care</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Medical Services</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Adult Day Care</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Pharmacy Services</a></li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-lg font-semibold mb-4">Support</h3>
            <ul className="space-y-2 text-gray-400">
              <li><a href="#" className="hover:text-white transition-colors">Help Center</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Emergency Support</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Contact Us</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Privacy Policy</a></li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-lg font-semibold mb-4">Contact</h3>
            <div className="space-y-2 text-gray-400">
              <div className="flex items-center">
                <Phone className="w-4 h-4 mr-2" />
                <span>1-800-CARE-NOW</span>
              </div>
              <div className="flex items-center">
                <span>Available 24/7</span>
              </div>
            </div>
          </div>
        </div>
        
        <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
          <p>&copy; 2025 CareConnect. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {renderNavigation()}
      
      {currentView === 'home' && (
        <>
          {renderHomePage()}
          {renderFooter()}
        </>
      )}
      
      {currentView === 'search' && (
        <div className="min-h-screen py-8">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-6">
            <Button 
              variant="outline" 
              onClick={() => setCurrentView('home')}
              className="mb-4"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Home
            </Button>
          </div>
          <ProviderSearch />
        </div>
      )}
      
      {currentView === 'booking' && selectedProvider && selectedService && (
        <div className="min-h-screen py-8">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-6">
            <Button 
              variant="outline" 
              onClick={() => setCurrentView('search')}
              className="mb-4"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Search
            </Button>
          </div>
          <BookingForm 
            provider={selectedProvider}
            service={selectedService}
            onBookingComplete={handleBookingComplete}
          />
        </div>
      )}
    </div>
  )
}

export default App
