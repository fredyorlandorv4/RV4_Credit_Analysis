# database.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import enum

db = SQLAlchemy()

class UserRole(enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.EMPLOYEE)
    department = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationship with applications
    applications = db.relationship('Application', backref='agent', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def total_applications(self):
        return self.applications.count()
    
    @property
    def active_applications(self):
        return self.applications.filter_by(status='In-Process').count()
    
    @property
    def approved_applications(self):
        return self.applications.filter_by(status='Approved').count()

class Application(db.Model):
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.String(50), unique=True, nullable=False)
    
    # Client Information
    client_name = db.Column(db.String(100), nullable=False)
    dpi = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    
    # Application Details
    application_type = db.Column(db.String(50), nullable=False)
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Personal Information
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    marital_status = db.Column(db.String(20))
    
    # Financial Information
    monthly_income = db.Column(db.Float)
    credit_score = db.Column(db.Integer)
    dti_ratio = db.Column(db.Float)
    employment_status = db.Column(db.String(50))
    employment_duration_months = db.Column(db.Integer)
    
    # Loan Details
    loan_amount = db.Column(db.Float)
    property_price = db.Column(db.Float)
    down_payment = db.Column(db.Float)
    interest_rate = db.Column(db.Float)
    loan_duration = db.Column(db.Integer)  # in years
    product_type = db.Column(db.String(50))
    
    # Processing Information
    status = db.Column(db.String(20), default='In-Process')  # In-Process, Approved, Declined, Withdrawn
    loan_decision = db.Column(db.String(20))  # Approved, Declined, Conditional
    processing_time_days = db.Column(db.Integer, default=0)
    documents_submitted = db.Column(db.Integer, default=0)
    completeness_score = db.Column(db.Float, default=0)
    
    # Risk Metrics
    approval_probability = db.Column(db.Float)
    withdrawal_risk = db.Column(db.Float)
    
    # Communication
    communication_frequency = db.Column(db.Float, default=1.0)
    last_contact_date = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    
    # Foreign Keys
    agent_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    documents = db.relationship('Document', backref='application', lazy='dynamic', cascade='all, delete-orphan')
    activities = db.relationship('ActivityLog', backref='application', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'application_id': self.application_id,
            'client_name': self.client_name,
            'dpi': self.dpi,
            'status': self.status,
            'loan_amount': self.loan_amount,
            'application_date': self.application_date.strftime('%Y-%m-%d') if self.application_date else None,
            'agent': self.agent.get_full_name() if self.agent else None,
            'approval_probability': self.approval_probability,
            'withdrawal_risk': self.withdrawal_risk
        }

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)
    document_name = db.Column(db.String(100))
    is_received = db.Column(db.Boolean, default=False)
    received_date = db.Column(db.DateTime)
    is_verified = db.Column(db.Boolean, default=False)
    verified_date = db.Column(db.DateTime)
    verified_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    notes = db.Column(db.Text)
    
    # Define standard document types
    DOCUMENT_TYPES = [
        'doc_id',
        'doc_salary',
        'doc_bank_statement',
        'doc_tax_return',
        'doc_property_docs'
    ]

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=True)  # Allow NULL for system activities
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='activities')

class SystemSettings(db.Model):
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))

# Helper functions for database initialization
def init_database(app):
    """Initialize database with tables and default data"""
    with app.app_context():
        db.create_all()
        
        # Create default admin user if none exists
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@rv4.com',
                first_name='System',
                last_name='Administrator',
                role=UserRole.ADMIN,
                department='IT'
            )
            admin.set_password('admin123')  # Change this in production!
            db.session.add(admin)
            
        # Create sample employee if none exists
        if not User.query.filter_by(username='employee1').first():
            employee = User(
                username='employee1',
                email='employee1@rv4.com',
                first_name='John',
                last_name='Doe',
                role=UserRole.EMPLOYEE,
                department='Credit Analysis'
            )
            employee.set_password('password123')  # Change this in production!
            db.session.add(employee)
            
        db.session.commit()
        print("✅ Database initialized successfully!")

def create_application_from_form(form_data, user_id):
    """Create a new application from form data"""
    import datetime
    
    def safe_get(data, key, default=None, convert_type=None):
        """Safely get value from form data with type conversion"""
        value = data.get(key, default)
        if value is None or value == '':
            return default
        if convert_type:
            try:
                if convert_type == int:
                    return int(float(value))  # Handle decimal strings
                elif convert_type == float:
                    return float(value)
                else:
                    return convert_type(value)
            except (ValueError, TypeError):
                return default
        return value
    
    # Generate unique application ID
    current_time = datetime.datetime.now()
    app_id = f"RV4-{current_time.strftime('%Y%m%d%H%M%S')}-{user_id}"
    
    # Create application instance
    application = Application(
        application_id=app_id,
        agent_id=user_id,
        client_name=safe_get(form_data, 'client_name', ''),
        dpi=safe_get(form_data, 'dpi', ''),
        email=safe_get(form_data, 'email', ''),
        phone=safe_get(form_data, 'phone', ''),
        address=safe_get(form_data, 'address', ''),
        application_type=safe_get(form_data, 'application_type', 'Mortgage'),
        age=safe_get(form_data, 'age', None, int),
        gender=safe_get(form_data, 'gender', ''),
        marital_status=safe_get(form_data, 'marital_status', ''),
        monthly_income=safe_get(form_data, 'monthly_income', None, float),
        credit_score=safe_get(form_data, 'credit_score', None, int),
        dti_ratio=safe_get(form_data, 'dti_ratio', None, float),
        employment_status=safe_get(form_data, 'employment_status', ''),
        employment_duration_months=safe_get(form_data, 'employment_duration_months', None, int),
        loan_amount=safe_get(form_data, 'loan_amount', None, float),
        property_price=safe_get(form_data, 'property_price', None, float),
        down_payment=safe_get(form_data, 'down_payment', None, float),
        interest_rate=safe_get(form_data, 'interest_rate', None, float),
        loan_duration=safe_get(form_data, 'loan_duration', None, int),
        product_type=safe_get(form_data, 'product_type', ''),
        status='In-Process',
        documents_submitted=0,
        processing_time_days=0,
        communication_frequency=1.0
    )
    
    return application

def log_activity(application_id, user_id, action, description=None):
    """Log an activity for an application or system-level activity"""
    try:
        activity = ActivityLog(
            application_id=application_id,  # Can be None for system activities
            user_id=user_id,
            action=action,
            description=description
        )
        db.session.add(activity)
        db.session.flush()  # Flush to catch constraint errors before commit
        return True
    except Exception as e:
        db.session.rollback()  # Rollback on any error
        # If database constraint prevents NULL application_id, skip logging for system activities
        if application_id is None:
            print(f"Warning: Could not log system activity '{action}' - database constraint prevents NULL application_id")
            return False
        else:
            # Re-raise for application-specific activities
            print(f"Error logging activity: {e}")
            return False