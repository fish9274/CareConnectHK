from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum

db = SQLAlchemy()

class UserRole(Enum):
    FAMILY = "family"
    PROVIDER = "provider"
    ADMIN = "admin"

class ProviderType(Enum):
    INDIVIDUAL = "individual"
    FACILITY = "facility"
    PHARMACY = "pharmacy"
    HOSPITAL = "hospital"

class ServiceType(Enum):
    HOME_CARE = "home_care"
    MEDICAL_SERVICES = "medical_services"
    ADULT_DAY_CARE = "adult_day_care"
    PHARMACY_SERVICES = "pharmacy_services"
    COMPANIONSHIP = "companionship"
    TRANSPORTATION = "transportation"

class BookingStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.FAMILY)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    family_profile = db.relationship('FamilyProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    provider_profile = db.relationship('ProviderProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    bookings = db.relationship('Booking', foreign_keys='Booking.family_user_id', backref='family_user', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'role': self.role.value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }

class FamilyProfile(db.Model):
    __tablename__ = 'family_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(50))
    zip_code = db.Column(db.String(10))
    emergency_contact_name = db.Column(db.String(100))
    emergency_contact_phone = db.Column(db.String(20))
    
    # Relationships
    elders = db.relationship('Elder', backref='family_profile', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'emergency_contact_name': self.emergency_contact_name,
            'emergency_contact_phone': self.emergency_contact_phone
        }

class Elder(db.Model):
    __tablename__ = 'elders'
    
    id = db.Column(db.Integer, primary_key=True)
    family_profile_id = db.Column(db.Integer, db.ForeignKey('family_profiles.id'), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    medical_conditions = db.Column(db.Text)
    medications = db.Column(db.Text)
    mobility_level = db.Column(db.String(50))
    care_preferences = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    care_plans = db.relationship('CarePlan', backref='elder', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'family_profile_id': self.family_profile_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'medical_conditions': self.medical_conditions,
            'medications': self.medications,
            'mobility_level': self.mobility_level,
            'care_preferences': self.care_preferences,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ProviderProfile(db.Model):
    __tablename__ = 'provider_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    provider_type = db.Column(db.Enum(ProviderType), nullable=False)
    business_name = db.Column(db.String(200))
    license_number = db.Column(db.String(100))
    certifications = db.Column(db.Text)
    specialties = db.Column(db.Text)
    description = db.Column(db.Text)
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(50))
    zip_code = db.Column(db.String(10))
    hourly_rate = db.Column(db.Numeric(10, 2))
    daily_rate = db.Column(db.Numeric(10, 2))
    is_verified = db.Column(db.Boolean, default=False)
    verification_date = db.Column(db.DateTime)
    rating = db.Column(db.Float, default=0.0)
    total_reviews = db.Column(db.Integer, default=0)
    availability_schedule = db.Column(db.Text)  # JSON string for schedule
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    services = db.relationship('Service', backref='provider', cascade='all, delete-orphan')
    bookings = db.relationship('Booking', foreign_keys='Booking.provider_id', backref='provider', cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='provider', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'provider_type': self.provider_type.value,
            'business_name': self.business_name,
            'license_number': self.license_number,
            'certifications': self.certifications,
            'specialties': self.specialties,
            'description': self.description,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'hourly_rate': float(self.hourly_rate) if self.hourly_rate else None,
            'daily_rate': float(self.daily_rate) if self.daily_rate else None,
            'is_verified': self.is_verified,
            'verification_date': self.verification_date.isoformat() if self.verification_date else None,
            'rating': self.rating,
            'total_reviews': self.total_reviews,
            'availability_schedule': self.availability_schedule,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Service(db.Model):
    __tablename__ = 'services'
    
    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('provider_profiles.id'), nullable=False)
    service_type = db.Column(db.Enum(ServiceType), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2))
    duration_minutes = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'provider_id': self.provider_id,
            'service_type': self.service_type.value,
            'name': self.name,
            'description': self.description,
            'price': float(self.price) if self.price else None,
            'duration_minutes': self.duration_minutes,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    family_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('provider_profiles.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    elder_id = db.Column(db.Integer, db.ForeignKey('elders.id'), nullable=False)
    scheduled_date = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(BookingStatus), default=BookingStatus.PENDING)
    total_cost = db.Column(db.Numeric(10, 2))
    special_instructions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    service = db.relationship('Service', backref='bookings')
    elder = db.relationship('Elder', backref='bookings')

    def to_dict(self):
        return {
            'id': self.id,
            'family_user_id': self.family_user_id,
            'provider_id': self.provider_id,
            'service_id': self.service_id,
            'elder_id': self.elder_id,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'duration_minutes': self.duration_minutes,
            'status': self.status.value,
            'total_cost': float(self.total_cost) if self.total_cost else None,
            'special_instructions': self.special_instructions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class CarePlan(db.Model):
    __tablename__ = 'care_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    elder_id = db.Column(db.Integer, db.ForeignKey('elders.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    care_goals = db.Column(db.Text)
    medication_schedule = db.Column(db.Text)  # JSON string
    activity_schedule = db.Column(db.Text)  # JSON string
    emergency_contacts = db.Column(db.Text)  # JSON string
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'elder_id': self.elder_id,
            'name': self.name,
            'description': self.description,
            'care_goals': self.care_goals,
            'medication_schedule': self.medication_schedule,
            'activity_schedule': self.activity_schedule,
            'emergency_contacts': self.emergency_contacts,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('provider_profiles.id'), nullable=False)
    family_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    booking = db.relationship('Booking', backref='review', uselist=False)
    family_user = db.relationship('User', backref='reviews_given')

    def to_dict(self):
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'provider_id': self.provider_id,
            'family_user_id': self.family_user_id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'))
    subject = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_messages')
    booking = db.relationship('Booking', backref='messages')

    def to_dict(self):
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'recipient_id': self.recipient_id,
            'booking_id': self.booking_id,
            'subject': self.subject,
            'content': self.content,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
