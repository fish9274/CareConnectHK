from flask import Blueprint, request, jsonify
from src.models.care_models import db, Booking, BookingStatus, ProviderProfile, Service, Elder, User
from datetime import datetime
import json

bookings_bp = Blueprint('bookings', __name__)

@bookings_bp.route('/bookings', methods=['POST'])
def create_booking():
    """Create a new booking"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['family_user_id', 'provider_id', 'service_id', 'elder_id', 'scheduled_date', 'duration_minutes']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate that the entities exist
        family_user = User.query.get(data['family_user_id'])
        if not family_user:
            return jsonify({'error': 'Family user not found'}), 404
        
        provider = ProviderProfile.query.get(data['provider_id'])
        if not provider:
            return jsonify({'error': 'Provider not found'}), 404
        
        service = Service.query.get(data['service_id'])
        if not service or not service.is_active:
            return jsonify({'error': 'Service not found or inactive'}), 404
        
        elder = Elder.query.get(data['elder_id'])
        if not elder:
            return jsonify({'error': 'Elder not found'}), 404
        
        # Validate that the service belongs to the provider
        if service.provider_id != data['provider_id']:
            return jsonify({'error': 'Service does not belong to the specified provider'}), 400
        
        # Parse scheduled date
        try:
            scheduled_date = datetime.fromisoformat(data['scheduled_date'])
        except ValueError:
            return jsonify({'error': 'Invalid scheduled_date format. Use ISO format.'}), 400
        
        # Check for scheduling conflicts
        existing_booking = Booking.query.filter(
            Booking.provider_id == data['provider_id'],
            Booking.scheduled_date == scheduled_date,
            Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.IN_PROGRESS])
        ).first()
        
        if existing_booking:
            return jsonify({'error': 'Provider is not available at the requested time'}), 409
        
        # Calculate total cost
        total_cost = 0
        if service.price:
            total_cost = service.price * (data['duration_minutes'] / 60)  # Assuming hourly pricing
        
        # Create the booking
        booking = Booking(
            family_user_id=data['family_user_id'],
            provider_id=data['provider_id'],
            service_id=data['service_id'],
            elder_id=data['elder_id'],
            scheduled_date=scheduled_date,
            duration_minutes=data['duration_minutes'],
            total_cost=total_cost,
            special_instructions=data.get('special_instructions', ''),
            status=BookingStatus.PENDING
        )
        
        db.session.add(booking)
        db.session.commit()
        
        # Return the created booking with related data
        booking_data = booking.to_dict()
        booking_data['service'] = service.to_dict()
        booking_data['provider'] = provider.to_dict()
        booking_data['elder'] = elder.to_dict()
        
        return jsonify(booking_data), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bookings_bp.route('/bookings/<int:booking_id>', methods=['GET'])
def get_booking(booking_id):
    """Get detailed booking information"""
    try:
        booking = Booking.query.get_or_404(booking_id)
        
        booking_data = booking.to_dict()
        booking_data['service'] = booking.service.to_dict()
        booking_data['provider'] = booking.provider.to_dict()
        booking_data['provider']['user'] = booking.provider.user.to_dict()
        booking_data['elder'] = booking.elder.to_dict()
        booking_data['family_user'] = booking.family_user.to_dict()
        
        return jsonify(booking_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bookings_bp.route('/bookings/<int:booking_id>', methods=['PUT'])
def update_booking(booking_id):
    """Update booking details"""
    try:
        booking = Booking.query.get_or_404(booking_id)
        data = request.get_json()
        
        # Only allow updates to certain fields
        updatable_fields = ['scheduled_date', 'duration_minutes', 'special_instructions', 'status']
        
        for field in updatable_fields:
            if field in data:
                if field == 'scheduled_date':
                    try:
                        booking.scheduled_date = datetime.fromisoformat(data[field])
                    except ValueError:
                        return jsonify({'error': 'Invalid scheduled_date format. Use ISO format.'}), 400
                elif field == 'status':
                    try:
                        booking.status = BookingStatus(data[field])
                    except ValueError:
                        return jsonify({'error': 'Invalid status value'}), 400
                else:
                    setattr(booking, field, data[field])
        
        # Recalculate total cost if duration changed
        if 'duration_minutes' in data and booking.service.price:
            booking.total_cost = booking.service.price * (booking.duration_minutes / 60)
        
        booking.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(booking.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bookings_bp.route('/bookings/<int:booking_id>/status', methods=['PUT'])
def update_booking_status(booking_id):
    """Update booking status"""
    try:
        booking = Booking.query.get_or_404(booking_id)
        data = request.get_json()
        
        if 'status' not in data:
            return jsonify({'error': 'Status is required'}), 400
        
        try:
            new_status = BookingStatus(data['status'])
        except ValueError:
            return jsonify({'error': 'Invalid status value'}), 400
        
        # Validate status transitions
        valid_transitions = {
            BookingStatus.PENDING: [BookingStatus.CONFIRMED, BookingStatus.CANCELLED],
            BookingStatus.CONFIRMED: [BookingStatus.IN_PROGRESS, BookingStatus.CANCELLED],
            BookingStatus.IN_PROGRESS: [BookingStatus.COMPLETED, BookingStatus.CANCELLED],
            BookingStatus.COMPLETED: [],  # Final state
            BookingStatus.CANCELLED: []   # Final state
        }
        
        if new_status not in valid_transitions.get(booking.status, []):
            return jsonify({'error': f'Invalid status transition from {booking.status.value} to {new_status.value}'}), 400
        
        booking.status = new_status
        booking.updated_at = datetime.utcnow()
        
        # Add status change reason if provided
        if 'reason' in data:
            # In a real application, you might want to log status changes
            pass
        
        db.session.commit()
        
        return jsonify(booking.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bookings_bp.route('/bookings', methods=['GET'])
def get_bookings():
    """Get bookings with filtering options"""
    try:
        # Get query parameters
        family_user_id = request.args.get('family_user_id', type=int)
        provider_id = request.args.get('provider_id', type=int)
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Build query
        query = Booking.query
        
        if family_user_id:
            query = query.filter(Booking.family_user_id == family_user_id)
        
        if provider_id:
            query = query.filter(Booking.provider_id == provider_id)
        
        if status:
            try:
                status_enum = BookingStatus(status)
                query = query.filter(Booking.status == status_enum)
            except ValueError:
                return jsonify({'error': 'Invalid status value'}), 400
        
        if start_date:
            try:
                start_date_obj = datetime.fromisoformat(start_date)
                query = query.filter(Booking.scheduled_date >= start_date_obj)
            except ValueError:
                return jsonify({'error': 'Invalid start_date format'}), 400
        
        if end_date:
            try:
                end_date_obj = datetime.fromisoformat(end_date)
                query = query.filter(Booking.scheduled_date <= end_date_obj)
            except ValueError:
                return jsonify({'error': 'Invalid end_date format'}), 400
        
        # Order by scheduled date
        query = query.order_by(Booking.scheduled_date.desc())
        
        # Execute query with pagination
        bookings = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        result = []
        for booking in bookings.items:
            booking_data = booking.to_dict()
            booking_data['service'] = booking.service.to_dict()
            booking_data['provider'] = {
                'id': booking.provider.id,
                'business_name': booking.provider.business_name,
                'provider_type': booking.provider.provider_type.value,
                'rating': booking.provider.rating,
                'is_verified': booking.provider.is_verified
            }
            booking_data['elder'] = {
                'id': booking.elder.id,
                'first_name': booking.elder.first_name,
                'last_name': booking.elder.last_name
            }
            result.append(booking_data)
        
        return jsonify({
            'bookings': result,
            'pagination': {
                'page': bookings.page,
                'pages': bookings.pages,
                'per_page': bookings.per_page,
                'total': bookings.total,
                'has_next': bookings.has_next,
                'has_prev': bookings.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bookings_bp.route('/bookings/<int:booking_id>', methods=['DELETE'])
def cancel_booking(booking_id):
    """Cancel a booking"""
    try:
        booking = Booking.query.get_or_404(booking_id)
        
        # Only allow cancellation if booking is not completed
        if booking.status in [BookingStatus.COMPLETED]:
            return jsonify({'error': 'Cannot cancel a completed booking'}), 400
        
        booking.status = BookingStatus.CANCELLED
        booking.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': 'Booking cancelled successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bookings_bp.route('/bookings/upcoming', methods=['GET'])
def get_upcoming_bookings():
    """Get upcoming bookings for a user"""
    try:
        user_id = request.args.get('user_id', type=int)
        user_type = request.args.get('user_type')  # 'family' or 'provider'
        
        if not user_id or not user_type:
            return jsonify({'error': 'user_id and user_type are required'}), 400
        
        current_time = datetime.utcnow()
        
        if user_type == 'family':
            query = Booking.query.filter(
                Booking.family_user_id == user_id,
                Booking.scheduled_date > current_time,
                Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.PENDING])
            )
        elif user_type == 'provider':
            query = Booking.query.filter(
                Booking.provider_id == user_id,
                Booking.scheduled_date > current_time,
                Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.PENDING])
            )
        else:
            return jsonify({'error': 'Invalid user_type. Must be "family" or "provider"'}), 400
        
        bookings = query.order_by(Booking.scheduled_date.asc()).limit(10).all()
        
        result = []
        for booking in bookings:
            booking_data = booking.to_dict()
            booking_data['service'] = booking.service.to_dict()
            if user_type == 'family':
                booking_data['provider'] = {
                    'id': booking.provider.id,
                    'business_name': booking.provider.business_name,
                    'provider_type': booking.provider.provider_type.value
                }
            else:
                booking_data['family_user'] = {
                    'id': booking.family_user.id,
                    'first_name': booking.family_user.first_name,
                    'last_name': booking.family_user.last_name
                }
            booking_data['elder'] = {
                'id': booking.elder.id,
                'first_name': booking.elder.first_name,
                'last_name': booking.elder.last_name
            }
            result.append(booking_data)
        
        return jsonify({'upcoming_bookings': result}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
