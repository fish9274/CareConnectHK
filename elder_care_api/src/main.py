import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from src.models.care_models import db
from src.routes.user import user_bp
from src.routes.providers import providers_bp
from src.routes.bookings import bookings_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for all routes
CORS(app)

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(providers_bp, url_prefix='/api')
app.register_blueprint(bookings_bp, url_prefix='/api')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()
    
    # Add sample data if database is empty
    from src.models.care_models import User, ProviderProfile, Service, Elder, FamilyProfile, UserRole, ProviderType, ServiceType
    from werkzeug.security import generate_password_hash
    from datetime import datetime, date
    import json
    
    if User.query.count() == 0:
        # Create sample family user
        family_user = User(
            username='johnson_family',
            email='mary.johnson@email.com',
            password_hash=generate_password_hash('password123'),
            first_name='Mary',
            last_name='Johnson',
            phone='555-0123',
            role=UserRole.FAMILY
        )
        db.session.add(family_user)
        db.session.flush()
        
        # Create family profile
        family_profile = FamilyProfile(
            user_id=family_user.id,
            address='123 Main St',
            city='Downtown',
            state='CA',
            zip_code='90210',
            emergency_contact_name='John Johnson',
            emergency_contact_phone='555-0124'
        )
        db.session.add(family_profile)
        db.session.flush()
        
        # Create elder
        elder = Elder(
            family_profile_id=family_profile.id,
            first_name='Robert',
            last_name='Johnson',
            date_of_birth=date(1940, 5, 15),
            gender='Male',
            medical_conditions='Diabetes, Hypertension',
            medications='Metformin, Lisinopril',
            mobility_level='Limited',
            care_preferences='Prefers morning appointments'
        )
        db.session.add(elder)
        
        # Create sample provider users
        providers_data = [
            {
                'username': 'sarah_johnson_rn',
                'email': 'sarah.johnson@caregivers.com',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'phone': '555-0201',
                'business_name': 'Sarah Johnson, RN',
                'provider_type': ProviderType.INDIVIDUAL,
                'license_number': 'RN123456',
                'certifications': 'Registered Nurse, CPR Certified',
                'specialties': 'Medication Management, Wound Care, Companionship',
                'description': 'Experienced registered nurse with 10+ years in elder care',
                'city': 'Downtown',
                'state': 'CA',
                'zip_code': '90210',
                'hourly_rate': 45.00,
                'rating': 4.9,
                'total_reviews': 127,
                'is_verified': True,
                'verification_date': datetime.utcnow(),
                'services': [
                    {'name': 'In-Home Nursing Care', 'service_type': ServiceType.MEDICAL_SERVICES, 'price': 45.00, 'duration': 60},
                    {'name': 'Medication Management', 'service_type': ServiceType.MEDICAL_SERVICES, 'price': 40.00, 'duration': 30},
                    {'name': 'Companionship', 'service_type': ServiceType.HOME_CARE, 'price': 35.00, 'duration': 120}
                ]
            },
            {
                'username': 'sunshine_senior_center',
                'email': 'info@sunshinesenior.com',
                'first_name': 'Sunshine',
                'last_name': 'Center',
                'phone': '555-0301',
                'business_name': 'Sunshine Senior Center',
                'provider_type': ProviderType.FACILITY,
                'license_number': 'FAC789012',
                'certifications': 'State Licensed Adult Day Care',
                'specialties': 'Social Activities, Meals, Transportation',
                'description': 'Premier adult day care facility with comprehensive programs',
                'city': 'Westside',
                'state': 'CA',
                'zip_code': '90211',
                'daily_rate': 65.00,
                'rating': 4.8,
                'total_reviews': 89,
                'is_verified': True,
                'verification_date': datetime.utcnow(),
                'services': [
                    {'name': 'Adult Day Care', 'service_type': ServiceType.ADULT_DAY_CARE, 'price': 65.00, 'duration': 480},
                    {'name': 'Transportation Service', 'service_type': ServiceType.TRANSPORTATION, 'price': 25.00, 'duration': 60}
                ]
            },
            {
                'username': 'michael_chen_cna',
                'email': 'michael.chen@homecare.com',
                'first_name': 'Michael',
                'last_name': 'Chen',
                'phone': '555-0401',
                'business_name': 'Michael Chen, CNA',
                'provider_type': ProviderType.INDIVIDUAL,
                'license_number': 'CNA345678',
                'certifications': 'Certified Nursing Assistant, First Aid',
                'specialties': 'Personal Hygiene, Mobility Assistance, Light Housekeeping',
                'description': 'Compassionate CNA specializing in personal care assistance',
                'city': 'Northside',
                'state': 'CA',
                'zip_code': '90212',
                'hourly_rate': 35.00,
                'rating': 4.7,
                'total_reviews': 156,
                'is_verified': True,
                'verification_date': datetime.utcnow(),
                'services': [
                    {'name': 'Personal Care Assistance', 'service_type': ServiceType.HOME_CARE, 'price': 35.00, 'duration': 120},
                    {'name': 'Mobility Assistance', 'service_type': ServiceType.HOME_CARE, 'price': 35.00, 'duration': 60},
                    {'name': 'Light Housekeeping', 'service_type': ServiceType.HOME_CARE, 'price': 30.00, 'duration': 90}
                ]
            }
        ]
        
        for provider_data in providers_data:
            # Create provider user
            provider_user = User(
                username=provider_data['username'],
                email=provider_data['email'],
                password_hash=generate_password_hash('password123'),
                first_name=provider_data['first_name'],
                last_name=provider_data['last_name'],
                phone=provider_data['phone'],
                role=UserRole.PROVIDER
            )
            db.session.add(provider_user)
            db.session.flush()
            
            # Create provider profile
            provider_profile = ProviderProfile(
                user_id=provider_user.id,
                provider_type=provider_data['provider_type'],
                business_name=provider_data['business_name'],
                license_number=provider_data['license_number'],
                certifications=provider_data['certifications'],
                specialties=provider_data['specialties'],
                description=provider_data['description'],
                city=provider_data['city'],
                state=provider_data['state'],
                zip_code=provider_data['zip_code'],
                hourly_rate=provider_data.get('hourly_rate'),
                daily_rate=provider_data.get('daily_rate'),
                rating=provider_data['rating'],
                total_reviews=provider_data['total_reviews'],
                is_verified=provider_data['is_verified'],
                verification_date=provider_data['verification_date'],
                availability_schedule=json.dumps({
                    'monday': {'start': '09:00', 'end': '17:00'},
                    'tuesday': {'start': '09:00', 'end': '17:00'},
                    'wednesday': {'start': '09:00', 'end': '17:00'},
                    'thursday': {'start': '09:00', 'end': '17:00'},
                    'friday': {'start': '09:00', 'end': '17:00'},
                    'saturday': {'start': '10:00', 'end': '16:00'},
                    'sunday': {'start': '10:00', 'end': '16:00'}
                })
            )
            db.session.add(provider_profile)
            db.session.flush()
            
            # Create services for the provider
            for service_data in provider_data['services']:
                service = Service(
                    provider_id=provider_profile.id,
                    service_type=service_data['service_type'],
                    name=service_data['name'],
                    description=f"Professional {service_data['name'].lower()} service",
                    price=service_data['price'],
                    duration_minutes=service_data['duration'],
                    is_active=True
                )
                db.session.add(service)
        
        db.session.commit()
        print("Sample data created successfully!")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Elder Care API is running',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
