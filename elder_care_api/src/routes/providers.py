from flask import Blueprint, request, jsonify
from src.models.care_models import db, ProviderProfile, Service, Review, User, ServiceType, ProviderType
from sqlalchemy import and_, or_
from datetime import datetime
import json

providers_bp = Blueprint('providers', __name__)

@providers_bp.route('/providers', methods=['GET'])
def get_providers():
    """Get all providers with optional filtering"""
    try:
        # Get query parameters
        provider_type = request.args.get('type')
        service_type = request.args.get('service_type')
        city = request.args.get('city')
        state = request.args.get('state')
        min_rating = request.args.get('min_rating', type=float)
        verified_only = request.args.get('verified_only', type=bool, default=False)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Build query
        query = ProviderProfile.query.join(User).filter(User.is_active == True)
        
        if provider_type:
            query = query.filter(ProviderProfile.provider_type == ProviderType(provider_type))
        
        if city:
            query = query.filter(ProviderProfile.city.ilike(f'%{city}%'))
            
        if state:
            query = query.filter(ProviderProfile.state.ilike(f'%{state}%'))
            
        if min_rating:
            query = query.filter(ProviderProfile.rating >= min_rating)
            
        if verified_only:
            query = query.filter(ProviderProfile.is_verified == True)
        
        if service_type:
            query = query.join(Service).filter(
                and_(
                    Service.service_type == ServiceType(service_type),
                    Service.is_active == True
                )
            )
        
        # Execute query with pagination
        providers = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        result = []
        for provider in providers.items:
            provider_data = provider.to_dict()
            # Add user information
            provider_data['user'] = provider.user.to_dict()
            # Add services
            provider_data['services'] = [service.to_dict() for service in provider.services if service.is_active]
            result.append(provider_data)
        
        return jsonify({
            'providers': result,
            'pagination': {
                'page': providers.page,
                'pages': providers.pages,
                'per_page': providers.per_page,
                'total': providers.total,
                'has_next': providers.has_next,
                'has_prev': providers.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@providers_bp.route('/providers/<int:provider_id>', methods=['GET'])
def get_provider(provider_id):
    """Get detailed provider information"""
    try:
        provider = ProviderProfile.query.get_or_404(provider_id)
        
        provider_data = provider.to_dict()
        provider_data['user'] = provider.user.to_dict()
        provider_data['services'] = [service.to_dict() for service in provider.services if service.is_active]
        
        # Get recent reviews
        recent_reviews = Review.query.filter_by(provider_id=provider_id)\
            .order_by(Review.created_at.desc())\
            .limit(10)\
            .all()
        
        provider_data['recent_reviews'] = []
        for review in recent_reviews:
            review_data = review.to_dict()
            review_data['family_user'] = {
                'first_name': review.family_user.first_name,
                'last_name': review.family_user.last_name[0] + '.'  # Privacy protection
            }
            provider_data['recent_reviews'].append(review_data)
        
        return jsonify(provider_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@providers_bp.route('/providers/search', methods=['POST'])
def search_providers():
    """Advanced provider search with multiple criteria"""
    try:
        data = request.get_json()
        
        # Extract search criteria
        location = data.get('location', {})
        services_needed = data.get('services', [])
        availability = data.get('availability', {})
        budget_range = data.get('budget_range', {})
        preferences = data.get('preferences', {})
        
        # Build base query
        query = ProviderProfile.query.join(User).filter(User.is_active == True)
        
        # Location filtering
        if location.get('city'):
            query = query.filter(ProviderProfile.city.ilike(f"%{location['city']}%"))
        if location.get('state'):
            query = query.filter(ProviderProfile.state.ilike(f"%{location['state']}%"))
        if location.get('zip_code'):
            query = query.filter(ProviderProfile.zip_code == location['zip_code'])
        
        # Service filtering
        if services_needed:
            service_types = [ServiceType(service) for service in services_needed if service in [e.value for e in ServiceType]]
            query = query.join(Service).filter(
                and_(
                    Service.service_type.in_(service_types),
                    Service.is_active == True
                )
            )
        
        # Budget filtering
        if budget_range.get('min_hourly'):
            query = query.filter(ProviderProfile.hourly_rate >= budget_range['min_hourly'])
        if budget_range.get('max_hourly'):
            query = query.filter(ProviderProfile.hourly_rate <= budget_range['max_hourly'])
        
        # Preferences filtering
        if preferences.get('verified_only'):
            query = query.filter(ProviderProfile.is_verified == True)
        if preferences.get('min_rating'):
            query = query.filter(ProviderProfile.rating >= preferences['min_rating'])
        
        # Execute query
        providers = query.distinct().all()
        
        result = []
        for provider in providers:
            provider_data = provider.to_dict()
            provider_data['user'] = provider.user.to_dict()
            provider_data['services'] = [service.to_dict() for service in provider.services if service.is_active]
            
            # Calculate match score (simple implementation)
            match_score = calculate_match_score(provider, data)
            provider_data['match_score'] = match_score
            
            result.append(provider_data)
        
        # Sort by match score
        result.sort(key=lambda x: x['match_score'], reverse=True)
        
        return jsonify({
            'providers': result,
            'total_found': len(result)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@providers_bp.route('/providers/<int:provider_id>/availability', methods=['GET'])
def get_provider_availability(provider_id):
    """Get provider availability for a specific date range"""
    try:
        provider = ProviderProfile.query.get_or_404(provider_id)
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            return jsonify({'error': 'start_date and end_date are required'}), 400
        
        # Parse availability schedule (assuming JSON format)
        availability_schedule = {}
        if provider.availability_schedule:
            try:
                availability_schedule = json.loads(provider.availability_schedule)
            except json.JSONDecodeError:
                availability_schedule = {}
        
        # Get existing bookings for the date range
        from src.models.care_models import Booking, BookingStatus
        existing_bookings = Booking.query.filter(
            and_(
                Booking.provider_id == provider_id,
                Booking.scheduled_date >= datetime.fromisoformat(start_date),
                Booking.scheduled_date <= datetime.fromisoformat(end_date),
                Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.IN_PROGRESS])
            )
        ).all()
        
        # Calculate available time slots
        available_slots = calculate_available_slots(
            availability_schedule, 
            existing_bookings, 
            start_date, 
            end_date
        )
        
        return jsonify({
            'provider_id': provider_id,
            'availability_schedule': availability_schedule,
            'existing_bookings': [booking.to_dict() for booking in existing_bookings],
            'available_slots': available_slots
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@providers_bp.route('/providers/<int:provider_id>/reviews', methods=['GET'])
def get_provider_reviews(provider_id):
    """Get all reviews for a provider"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        reviews = Review.query.filter_by(provider_id=provider_id)\
            .order_by(Review.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        result = []
        for review in reviews.items:
            review_data = review.to_dict()
            review_data['family_user'] = {
                'first_name': review.family_user.first_name,
                'last_name': review.family_user.last_name[0] + '.'  # Privacy protection
            }
            result.append(review_data)
        
        return jsonify({
            'reviews': result,
            'pagination': {
                'page': reviews.page,
                'pages': reviews.pages,
                'per_page': reviews.per_page,
                'total': reviews.total,
                'has_next': reviews.has_next,
                'has_prev': reviews.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calculate_match_score(provider, search_criteria):
    """Calculate a match score for a provider based on search criteria"""
    score = 0
    
    # Base score for verified providers
    if provider.is_verified:
        score += 20
    
    # Rating score (0-25 points)
    score += (provider.rating / 5.0) * 25
    
    # Service match score
    services_needed = search_criteria.get('services', [])
    if services_needed:
        provider_services = [service.service_type.value for service in provider.services if service.is_active]
        matching_services = set(services_needed) & set(provider_services)
        service_match_ratio = len(matching_services) / len(services_needed)
        score += service_match_ratio * 30
    
    # Budget compatibility score
    budget_range = search_criteria.get('budget_range', {})
    if budget_range.get('max_hourly') and provider.hourly_rate:
        if provider.hourly_rate <= budget_range['max_hourly']:
            score += 15
    
    # Review count bonus
    if provider.total_reviews > 10:
        score += 10
    elif provider.total_reviews > 5:
        score += 5
    
    return min(score, 100)  # Cap at 100

def calculate_available_slots(availability_schedule, existing_bookings, start_date, end_date):
    """Calculate available time slots for a provider"""
    # This is a simplified implementation
    # In a real application, this would be more sophisticated
    
    available_slots = []
    
    # Default availability if no schedule is set
    if not availability_schedule:
        availability_schedule = {
            'monday': {'start': '09:00', 'end': '17:00'},
            'tuesday': {'start': '09:00', 'end': '17:00'},
            'wednesday': {'start': '09:00', 'end': '17:00'},
            'thursday': {'start': '09:00', 'end': '17:00'},
            'friday': {'start': '09:00', 'end': '17:00'},
            'saturday': {'start': '10:00', 'end': '16:00'},
            'sunday': {'start': '10:00', 'end': '16:00'}
        }
    
    # Generate sample available slots
    from datetime import datetime, timedelta
    current_date = datetime.fromisoformat(start_date)
    end_date_obj = datetime.fromisoformat(end_date)
    
    while current_date <= end_date_obj:
        day_name = current_date.strftime('%A').lower()
        if day_name in availability_schedule:
            day_schedule = availability_schedule[day_name]
            # Add morning slot
            available_slots.append({
                'date': current_date.date().isoformat(),
                'start_time': day_schedule.get('start', '09:00'),
                'end_time': '12:00',
                'available': True
            })
            # Add afternoon slot
            available_slots.append({
                'date': current_date.date().isoformat(),
                'start_time': '13:00',
                'end_time': day_schedule.get('end', '17:00'),
                'available': True
            })
        
        current_date += timedelta(days=1)
    
    return available_slots
