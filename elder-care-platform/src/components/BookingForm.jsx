import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Calendar } from '@/components/ui/calendar.jsx'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover.jsx'
import { 
  Calendar as CalendarIcon,
  Clock,
  DollarSign,
  User,
  CheckCircle,
  AlertCircle,
  Loader2
} from 'lucide-react'
import { format } from 'date-fns'

const BookingForm = ({ provider, service, onBookingComplete }) => {
  const [bookingData, setBookingData] = useState({
    elder_id: '',
    scheduled_date: null,
    scheduled_time: '',
    duration_minutes: service?.duration_minutes || 60,
    special_instructions: ''
  })
  const [elders, setElders] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  // Mock elder data - in a real app, this would come from the user's profile
  useEffect(() => {
    setElders([
      {
        id: 1,
        first_name: 'Robert',
        last_name: 'Johnson',
        age: 83,
        medical_conditions: 'Diabetes, Hypertension'
      }
    ])
  }, [])

  const timeSlots = [
    '08:00', '08:30', '09:00', '09:30', '10:00', '10:30',
    '11:00', '11:30', '12:00', '12:30', '13:00', '13:30',
    '14:00', '14:30', '15:00', '15:30', '16:00', '16:30',
    '17:00', '17:30', '18:00'
  ]

  const durationOptions = [
    { value: 30, label: '30 minutes' },
    { value: 60, label: '1 hour' },
    { value: 90, label: '1.5 hours' },
    { value: 120, label: '2 hours' },
    { value: 180, label: '3 hours' },
    { value: 240, label: '4 hours' },
    { value: 480, label: '8 hours (full day)' }
  ]

  const calculateTotalCost = () => {
    if (!service?.price || !bookingData.duration_minutes) return 0
    return (service.price * (bookingData.duration_minutes / 60)).toFixed(2)
  }

  const handleInputChange = (field, value) => {
    setBookingData(prev => ({
      ...prev,
      [field]: value
    }))
    setError('')
  }

  const handleDateSelect = (date) => {
    setBookingData(prev => ({
      ...prev,
      scheduled_date: date
    }))
    setError('')
  }

  const validateForm = () => {
    if (!bookingData.elder_id) {
      setError('Please select an elder to receive care')
      return false
    }
    if (!bookingData.scheduled_date) {
      setError('Please select a date')
      return false
    }
    if (!bookingData.scheduled_time) {
      setError('Please select a time')
      return false
    }
    if (!bookingData.duration_minutes) {
      setError('Please select a duration')
      return false
    }
    return true
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!validateForm()) return

    setLoading(true)
    setError('')

    try {
      // Combine date and time
      const scheduledDateTime = new Date(bookingData.scheduled_date)
      const [hours, minutes] = bookingData.scheduled_time.split(':')
      scheduledDateTime.setHours(parseInt(hours), parseInt(minutes))

      const bookingPayload = {
        family_user_id: 1, // Mock family user ID
        provider_id: provider.id,
        service_id: service.id,
        elder_id: parseInt(bookingData.elder_id),
        scheduled_date: scheduledDateTime.toISOString(),
        duration_minutes: bookingData.duration_minutes,
        special_instructions: bookingData.special_instructions
      }

      const response = await fetch('/api/bookings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(bookingPayload)
      })

      const data = await response.json()

      if (response.ok) {
        setSuccess(true)
        if (onBookingComplete) {
          onBookingComplete(data)
        }
      } else {
        setError(data.error || 'Failed to create booking')
      }
    } catch (error) {
      setError('Network error. Please try again.')
      console.error('Booking error:', error)
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <Card className="max-w-md mx-auto">
        <CardContent className="pt-6">
          <div className="text-center">
            <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Booking Confirmed!
            </h3>
            <p className="text-gray-600 mb-4">
              Your booking request has been submitted successfully. The provider will confirm your appointment shortly.
            </p>
            <Button onClick={() => setSuccess(false)} variant="outline">
              Book Another Service
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Book Service</CardTitle>
        <CardDescription>
          Schedule {service?.name} with {provider?.business_name || `${provider?.user?.first_name} ${provider?.user?.last_name}`}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Elder Selection */}
          <div>
            <Label htmlFor="elder">Select Elder</Label>
            <Select value={bookingData.elder_id} onValueChange={(value) => handleInputChange('elder_id', value)}>
              <SelectTrigger>
                <SelectValue placeholder="Choose who will receive care..." />
              </SelectTrigger>
              <SelectContent>
                {elders.map((elder) => (
                  <SelectItem key={elder.id} value={elder.id.toString()}>
                    <div className="flex items-center gap-2">
                      <User className="w-4 h-4" />
                      {elder.first_name} {elder.last_name} (Age {elder.age})
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Date Selection */}
          <div>
            <Label>Select Date</Label>
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  className="w-full justify-start text-left font-normal"
                >
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {bookingData.scheduled_date ? (
                    format(bookingData.scheduled_date, 'PPP')
                  ) : (
                    <span>Pick a date</span>
                  )}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0">
                <Calendar
                  mode="single"
                  selected={bookingData.scheduled_date}
                  onSelect={handleDateSelect}
                  disabled={(date) => date < new Date() || date < new Date("1900-01-01")}
                  initialFocus
                />
              </PopoverContent>
            </Popover>
          </div>

          {/* Time Selection */}
          <div>
            <Label htmlFor="time">Select Time</Label>
            <Select value={bookingData.scheduled_time} onValueChange={(value) => handleInputChange('scheduled_time', value)}>
              <SelectTrigger>
                <SelectValue placeholder="Choose a time..." />
              </SelectTrigger>
              <SelectContent>
                {timeSlots.map((time) => (
                  <SelectItem key={time} value={time}>
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4" />
                      {time}
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Duration Selection */}
          <div>
            <Label htmlFor="duration">Duration</Label>
            <Select 
              value={bookingData.duration_minutes.toString()} 
              onValueChange={(value) => handleInputChange('duration_minutes', parseInt(value))}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select duration..." />
              </SelectTrigger>
              <SelectContent>
                {durationOptions.map((option) => (
                  <SelectItem key={option.value} value={option.value.toString()}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Special Instructions */}
          <div>
            <Label htmlFor="instructions">Special Instructions (Optional)</Label>
            <Textarea
              id="instructions"
              placeholder="Any specific requirements or notes for the caregiver..."
              value={bookingData.special_instructions}
              onChange={(e) => handleInputChange('special_instructions', e.target.value)}
              rows={3}
            />
          </div>

          {/* Cost Summary */}
          <Card className="bg-gray-50">
            <CardContent className="pt-4">
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Service:</span>
                  <span className="font-medium">{service?.name}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Duration:</span>
                  <span className="font-medium">
                    {durationOptions.find(d => d.value === bookingData.duration_minutes)?.label || 'Not selected'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Rate:</span>
                  <span className="font-medium">${service?.price}/hour</span>
                </div>
                <div className="border-t pt-2 flex justify-between items-center">
                  <span className="font-semibold">Total Cost:</span>
                  <span className="font-bold text-lg flex items-center gap-1">
                    <DollarSign className="w-4 h-4" />
                    {calculateTotalCost()}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Error Message */}
          {error && (
            <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-md">
              <AlertCircle className="w-5 h-5 text-red-500" />
              <span className="text-red-700 text-sm">{error}</span>
            </div>
          )}

          {/* Submit Button */}
          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Creating Booking...
              </>
            ) : (
              <>
                Confirm Booking - ${calculateTotalCost()}
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}

export default BookingForm
