# app_updated.py - Complete Enhanced Version

import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, login_required, current_user
import plotly.io as pio
from datetime import datetime, timedelta
import tempfile

# Import database models and auth
from database import db, init_database, User, Application, Document, ActivityLog, create_application_from_form, log_activity
from auth import auth_bp

# Import enhanced model pipeline
from model_pipeline import model
from plotting import create_trends_chart, create_funnel_chart, create_correlation_heatmap, create_box_plot, create_sunburst_chart
from translations import get_text as _get_text
from sample_data import generate_and_save_data

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'a_very_secret_key_for_rv4_multilang_final'
# PostgreSQL connection - Local: 10.0.3.14:5432, Remote: 192.227.80.200:27018
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://app_user:rvH~}f781{}[@192.227.80.200:27018/app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Initialize database and models on first run
with app.app_context():
    init_database(app)
    
    # Create weights directory if it doesn't exist
    os.makedirs('weights', exist_ok=True)
    
    # Load existing models or train new ones
    if not model.load_models():
        print("No existing models found. Training on sample data...")
        DATA_FILE_PATH = 'data/credit_data.csv'
        if not os.path.exists(DATA_FILE_PATH):
            generate_and_save_data(DATA_FILE_PATH)
        df = pd.read_csv(DATA_FILE_PATH)
        model.train(df, source='initial_sample')

# --- CONFIGURATION ---
REQUIRED_DOCS = ['doc_id', 'doc_salary', 'doc_bank_statement', 'doc_tax_return', 'doc_property_docs']

# --- HELPER FUNCTIONS ---
def calculate_dti_ratio(loan_amount, interest_rate, loan_duration, monthly_income):
    """Calculate DTI ratio from loan parameters and monthly income"""
    try:
        if not all([loan_amount, interest_rate, loan_duration, monthly_income]) or monthly_income <= 0:
            return None
        
        # Calculate monthly payment
        monthly_rate = interest_rate / 100 / 12
        n_payments = loan_duration * 12
        
        if monthly_rate > 0:
            # Standard mortgage payment formula
            monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** n_payments) / ((1 + monthly_rate) ** n_payments - 1)
        else:
            # Zero interest case
            monthly_payment = loan_amount / n_payments if n_payments > 0 else 0
        
        # Calculate DTI ratio
        dti_ratio = monthly_payment / monthly_income
        return round(dti_ratio, 4)
        
    except (ValueError, ZeroDivisionError, TypeError):
        return None

def calculate_application_predictions(application):
    """Automatically calculate predictions for an application and update database"""
    try:
        # Ensure we have minimum required data
        if not application.monthly_income or application.monthly_income <= 0:
            return False, "Monthly income is required for predictions"
        
        if not application.credit_score or application.credit_score <= 0:
            return False, "Credit score is required for predictions"
        
        # Prepare data for prediction
        submitted_data = {
            'Age': application.age or 35,
            'Gender': application.gender or 'Male',
            'Credit_Score': application.credit_score or 650,
            'Monthly_Income': application.monthly_income or 35000,
            'DTI_Ratio': application.dti_ratio or 0.35,
            'Employment_Status': application.employment_status or 'Employed',
            'Documents_Submitted': application.documents_submitted or 0,
            'Employment_Duration_Months': application.employment_duration_months or 24,
            'Processing_Time_Days': max(application.processing_time_days or 1, 1),  # Ensure at least 1 day
            'completeness_score': application.completeness_score or 0,
            'Days_In_Process': max(application.processing_time_days or 1, 1),
            'Communication_Frequency': application.communication_frequency or 1.0,
            'Loan_Amount': application.loan_amount or 500000,
            'Property_Price': application.property_price or 750000,
            'Down_Payment': application.down_payment or 250000,
            'Interest_Rate': application.interest_rate or 7.5,
            'Loan_Duration': application.loan_duration or 20,
        }
        
        # Get predictions
        prediction_results = model.predict(submitted_data)
        
        # Update application with predictions (ensure values are within valid range)
        application.approval_probability = max(0, min(100, prediction_results.get('success_probability', 0)))
        application.withdrawal_risk = max(0, min(100, prediction_results.get('withdrawal_risk', 0)))
        
        # Log the prediction activity
        if current_user and current_user.is_authenticated:
            log_activity(
                application.id, 
                current_user.id,
                'PREDICTION_AUTO_CALCULATED', 
                f'Auto-calculated: Approval {application.approval_probability:.1f}%, Risk {application.withdrawal_risk:.1f}%'
            )
        
        return True, prediction_results
        
    except Exception as e:
        app.logger.error(f"Error calculating predictions for application {application.id}: {str(e)}")
        return False, str(e)

# --- LANGUAGE & CONTEXT ---
@app.before_request
def before_request():
    if 'language' not in session:
        session['language'] = 'es'

@app.context_processor
def inject_get_text():
    def get_text(key):
        return _get_text(session.get('language', 'en'), key)
    return dict(get_text=get_text)

@app.route('/change_language/<lang>')
def change_language(lang):
    if lang in ['en', 'es']:
        session['language'] = lang
    return redirect(request.referrer or url_for('dashboard'))

# --- MAIN ROUTES ---
@app.route('/')
def index():
    """Redirect to login or dashboard"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('auth.login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard with user-specific data and model info"""
    # Get applications for current user (or all if admin)
    if current_user.role.value == 'admin':
        applications = Application.query.all()
    else:
        applications = current_user.applications.all()
    
    # Convert to DataFrame for analysis
    if applications and len(applications) > 0:
        df_data = []
        for app in applications:
            df_data.append({
                'Application_ID': app.application_id,
                'Application_Date': app.application_date or datetime.utcnow(),
                'Age': app.age or 35,
                'Gender': app.gender or 'Male',
                'Monthly_Income': app.monthly_income or 35000,
                'Credit_Score': app.credit_score or 650,
                'DTI_Ratio': app.dti_ratio or 0.35,
                'Employment_Status': app.employment_status or 'Employed',
                'Processing_Time_Days': app.processing_time_days or 15,
                'Status': app.status or 'In-Process'
            })
        df_active = pd.DataFrame(df_data)
    else:
        # Use sample data if no real data exists
        try:
            df_active = pd.read_csv('data/credit_data.csv')
            if 'Application_Date' in df_active.columns:
                df_active['Application_Date'] = pd.to_datetime(df_active['Application_Date'])
        except:
            # Create minimal sample data
            df_active = pd.DataFrame({
                'Application_ID': ['SAMPLE-001', 'SAMPLE-002', 'SAMPLE-003'],
                'Application_Date': [datetime.utcnow() - timedelta(days=i*10) for i in range(3)],
                'Age': [35, 42, 28],
                'Gender': ['Male', 'Female', 'Male'],
                'Monthly_Income': [45000, 62000, 38000],
                'Credit_Score': [720, 680, 750],
                'DTI_Ratio': [0.32, 0.28, 0.45],
                'Employment_Status': ['Employed', 'Employed', 'Self-Employed'],
                'Processing_Time_Days': [15, 22, 18],
                'Status': ['Approved', 'In-Process', 'Approved']
            })
    
    # Calculate KPIs - Ensure values are calculated properly
    total_apps = len(df_active)
    approved_count = len(df_active[df_active['Status'] == 'Approved'])
    declined_count = len(df_active[df_active['Status'] == 'Declined'])
    
    kpis = {
        'total_apps': f"{total_apps:,}",
        'approval_rate': f"{(approved_count / total_apps * 100) if total_apps > 0 else 0:.1f}%",
        'rejection_rate': f"{(declined_count / total_apps * 100) if total_apps > 0 else 0:.1f}%",
        'avg_processing_time': f"{df_active['Processing_Time_Days'].mean() if total_apps > 0 else 0:.1f} days"
    }
    
    # Generate graphs - ensure data exists
    graphs = {}
    try:
        if len(df_active) > 0:
            graphs['trends'] = pio.to_json(create_trends_chart(df_active))
            graphs['funnel'] = pio.to_json(create_funnel_chart(df_active))
            
            if len(df_active) > 5:  # Need minimum data for correlation
                graphs['heatmap'] = pio.to_json(create_correlation_heatmap(df_active))
            else:
                graphs['heatmap'] = None
                
            graphs['box_plot'] = pio.to_json(create_box_plot(df_active))
            graphs['sunburst'] = pio.to_json(create_sunburst_chart(df_active))
        else:
            graphs = {
                'trends': None,
                'funnel': None,
                'heatmap': None,
                'box_plot': None,
                'sunburst': None
            }
    except Exception as e:
        print(f"ERROR generating charts: {str(e)}")
        graphs = {
            'trends': None,
            'funnel': None,
            'heatmap': None,
            'box_plot': None,
            'sunburst': None
        }
    
    # Get model information
    model_info = None
    try:
        info = model.get_model_info()
        if info.get('last_metrics'):
            model_info = {
                'last_trained': info.get('training_history', [{}])[-1].get('timestamp', 'Never') if info.get('training_history') else 'Never',
                'accuracy': round(info['last_metrics'].get('approval', {}).get('accuracy', 0) * 100, 1),
                'records_used': info.get('training_history', [{}])[-1].get('records', 0) if info.get('training_history') else 0
            }
    except Exception as e:
        app.logger.warning(f"Could not load model info: {e}")
    
    # Get recent applications for current user
    recent_apps = current_user.applications.order_by(Application.application_date.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         kpis=kpis, 
                         graphs=graphs, 
                         recent_apps=recent_apps,
                         user=current_user,
                         model_info=model_info)

@app.route('/my_clients')
@login_required
def my_clients():
    """View all clients for current user"""
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    search_query = request.args.get('search', '')
    
    # Base query
    query = current_user.applications
    
    # Apply filters
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    if search_query:
        query = query.filter(
            (Application.client_name.contains(search_query)) |
            (Application.dpi.contains(search_query)) |
            (Application.application_id.contains(search_query))
        )
    
    # Order by date
    applications = query.order_by(Application.application_date.desc()).all()
    
    return render_template('my_clients.html', applications=applications, user=current_user)

@app.route('/client/<int:app_id>')
@login_required
def client_detail(app_id):
    """View detailed client information"""
    application = Application.query.get_or_404(app_id)
    
    # Check permission (only owner or admin can view)
    if application.agent_id != current_user.id and current_user.role.value != 'admin':
        flash('You do not have permission to view this application', 'danger')
        return redirect(url_for('my_clients'))
    
    # Auto-calculate predictions if they don't exist
    if application.approval_probability is None or application.withdrawal_risk is None:
        prediction_success, prediction_result = calculate_application_predictions(application)
        if prediction_success:
            try:
                db.session.commit()
                app.logger.info(f"Auto-calculated missing predictions for application {application.application_id}")
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Failed to save auto-calculated predictions: {str(e)}")
        else:
            app.logger.warning(f"Could not auto-calculate predictions for {application.application_id}: {prediction_result}")
    
    # Get activity log
    activities = ActivityLog.query.filter_by(application_id=app_id).order_by(ActivityLog.timestamp.desc()).limit(10).all()
    
    # Get documents
    documents = Document.query.filter_by(application_id=app_id).all()
    
    return render_template('client_detail.html', 
                         application=application, 
                         activities=activities,
                         documents=documents,
                         user=current_user)

@app.route('/new_application', methods=['GET', 'POST'])
@login_required
def new_application():
    """Create a new application with DTI calculation"""
    if request.method == 'POST':
        try:
            # Calculate DTI and monthly payment
            form_data = request.form.to_dict()
            
            # Calculate DTI ratio using helper function
            loan_amount = float(form_data.get('loan_amount', 0))
            interest_rate = float(form_data.get('interest_rate', 0))
            loan_duration = float(form_data.get('loan_duration', 0))
            monthly_income = float(form_data.get('monthly_income', 1))
            
            # Calculate and store DTI ratio
            dti_ratio = calculate_dti_ratio(loan_amount, interest_rate, loan_duration, monthly_income)
            if dti_ratio is not None:
                form_data['dti_ratio'] = str(dti_ratio)
            else:
                # Use provided DTI or default
                if 'dti_ratio' not in form_data or not form_data['dti_ratio']:
                    form_data['dti_ratio'] = '0.35'
            
            # Create application from form data
            application = create_application_from_form(form_data, current_user.id)
            
            # Save to database
            db.session.add(application)
            db.session.flush()  # Get the ID
            
            # Create default documents
            for doc_type in REQUIRED_DOCS:
                doc = Document(
                    application_id=application.id,
                    document_type=doc_type,
                    document_name=_get_text(session.get('language', 'en'), doc_type),
                    is_received=False
                )
                db.session.add(doc)
            
            # Log activity
            log_activity(application.id, current_user.id, 'APPLICATION_CREATED', 
                        f'New application created for {application.client_name}')
            
            # Automatically calculate predictions for the new application
            prediction_success, prediction_result = calculate_application_predictions(application)
            if prediction_success:
                app.logger.info(f"Auto-calculated predictions for new application {application.application_id}")
            else:
                app.logger.warning(f"Could not auto-calculate predictions for {application.application_id}: {prediction_result}")
            
            db.session.commit()
            
            flash(f'Application {application.application_id} created successfully!', 'success')
            
            # Redirect to client detail page
            return redirect(url_for('client_detail', app_id=application.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating application: {str(e)}', 'danger')
            return render_template('new_application.html', form_data=request.form.to_dict())
    
    return render_template('new_application.html', form_data={})

@app.route('/update_application/<int:app_id>', methods=['POST'])
@login_required
def update_application(app_id):
    """Update application status and details"""
    application = Application.query.get_or_404(app_id)
    
    # Check permission
    if application.agent_id != current_user.id and current_user.role.value != 'admin':
        return jsonify({'error': 'Permission denied'}), 403
    
    try:
        # Update fields from form
        application.status = request.form.get('status', application.status)
        application.loan_decision = request.form.get('loan_decision', application.loan_decision)
        application.notes = request.form.get('notes', application.notes)
        
        # Update financial fields if provided and recalculate DTI
        financial_updated = False
        if 'loan_amount' in request.form:
            application.loan_amount = float(request.form.get('loan_amount', 0))
            financial_updated = True
        if 'interest_rate' in request.form:
            application.interest_rate = float(request.form.get('interest_rate', 0))
            financial_updated = True
        if 'loan_duration' in request.form:
            application.loan_duration = int(request.form.get('loan_duration', 0))
            financial_updated = True
        if 'monthly_income' in request.form:
            application.monthly_income = float(request.form.get('monthly_income', 0))
            financial_updated = True
        
        # Recalculate DTI if financial parameters were updated
        if financial_updated and application.loan_amount and application.interest_rate and application.loan_duration and application.monthly_income:
            new_dti = calculate_dti_ratio(
                application.loan_amount,
                application.interest_rate,
                application.loan_duration,
                application.monthly_income
            )
            if new_dti is not None:
                application.dti_ratio = new_dti
        
        application.last_updated = datetime.utcnow()
        
        # Log activity
        log_activity(application.id, current_user.id, 'APPLICATION_UPDATED', 
                    f'Status changed to {application.status}')
        
        # Recalculate predictions if financial data was updated
        if financial_updated:
            prediction_success, prediction_result = calculate_application_predictions(application)
            if prediction_success:
                log_activity(application.id, current_user.id, 'PREDICTIONS_UPDATED', 
                           'Predictions recalculated after financial update')
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Application updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/update_documents/<int:app_id>', methods=['POST'])
@login_required
def update_documents(app_id):
    """Update document status for an application"""
    application = Application.query.get_or_404(app_id)
    
    # Check permission
    if application.agent_id != current_user.id and current_user.role.value != 'admin':
        flash('Permission denied', 'danger')
        return redirect(url_for('my_clients'))
    
    try:
        # Get submitted documents from form
        submitted_docs = request.form.getlist('documents')
        
        # Update document status
        for doc in application.documents:
            doc.is_received = doc.document_type in submitted_docs
            if doc.is_received and not doc.received_date:
                doc.received_date = datetime.utcnow()
        
        # Update completeness score
        total_docs = len(REQUIRED_DOCS)
        received_docs = len(submitted_docs)
        application.completeness_score = (received_docs / total_docs * 100) if total_docs > 0 else 0
        application.documents_submitted = received_docs
        
        # Recalculate predictions since document completeness affects them
        prediction_success, prediction_result = calculate_application_predictions(application)
        if prediction_success:
            app.logger.info(f"Recalculated predictions after document update for {application.application_id}")
        else:
            app.logger.warning(f"Could not recalculate predictions: {prediction_result}")
        
        # Log activity
        log_activity(application.id, current_user.id, 'DOCUMENTS_UPDATED', 
                    f'Documents updated: {received_docs}/{total_docs} received')
        
        db.session.commit()
        
        flash('Documents updated successfully', 'success')
        return redirect(url_for('client_detail', app_id=app_id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating documents: {str(e)}', 'danger')
        return redirect(url_for('client_detail', app_id=app_id))

@app.route('/predictions', methods=['GET', 'POST'])
@login_required
def predictions():
    """ML predictions page with enhanced model and DTI calculation"""
    prediction_results = None
    submitted_data = {}
    
    if request.method == 'POST':
        # Check if this is for an existing application
        app_id = request.form.get('application_id')
        
        if app_id:
            # Load data from existing application
            application = Application.query.get(app_id)
            if application and (application.agent_id == current_user.id or current_user.role.value == 'admin'):
                submitted_data = {
                    'Age': application.age or 35,
                    'Gender': application.gender or 'Male',
                    'Credit_Score': application.credit_score or 650,
                    'Monthly_Income': application.monthly_income or 35000,
                    'DTI_Ratio': application.dti_ratio or 0.35,
                    'Employment_Status': application.employment_status or 'Employed',
                    'Documents_Submitted': application.documents_submitted or 4,
                    'Employment_Duration_Months': application.employment_duration_months or 24,
                    'Processing_Time_Days': application.processing_time_days or 15,
                    'completeness_score': application.completeness_score or 80,
                    'Days_In_Process': application.processing_time_days or 15,
                    'Communication_Frequency': application.communication_frequency or 0.5,
                    'Loan_Amount': application.loan_amount or 500000,
                    'Property_Price': application.property_price or 750000,
                    'Down_Payment': application.down_payment or 250000,
                    'Interest_Rate': application.interest_rate or 7.5,
                    'Loan_Duration': application.loan_duration or 20,
                }
        else:
            # Use form data for new prediction
            submitted_data = {
                'Age': request.form.get('Age', 35, type=int),
                'Gender': request.form.get('Gender', 'Male'),
                'Credit_Score': request.form.get('Credit_Score', 650, type=int),
                'Monthly_Income': request.form.get('Monthly_Income', 35000, type=float),
                'DTI_Ratio': request.form.get('DTI_Ratio', 0.35, type=float),
                'Employment_Status': request.form.get('Employment_Status', 'Employed'),
                'Documents_Submitted': request.form.get('Documents_Submitted', 4, type=int),
                'Employment_Duration_Months': request.form.get('Employment_Duration_Months', 24, type=int),
                'Processing_Time_Days': request.form.get('days_in_process', 15, type=int),
                'completeness_score': request.form.get('completeness_score', 80, type=float),
                'Days_In_Process': request.form.get('days_in_process', 15, type=int),
                'Communication_Frequency': request.form.get('Communication_Frequency', 0.5, type=float),
                'Loan_Amount': request.form.get('Loan_Amount', 500000, type=float),
                'Property_Price': request.form.get('Property_Price', 750000, type=float),
                'Down_Payment': request.form.get('Down_Payment', 250000, type=float),
                'Interest_Rate': request.form.get('Interest_Rate', 7.5, type=float),
                'Loan_Duration': request.form.get('Loan_Duration', 20, type=int),
            }
            
            # Calculate DTI if not provided (for manual predictions)
            calculated_dti = calculate_dti_ratio(
                submitted_data['Loan_Amount'],
                submitted_data['Interest_Rate'],
                submitted_data['Loan_Duration'],
                submitted_data['Monthly_Income']
            )
            if calculated_dti is not None:
                submitted_data['DTI_Ratio'] = calculated_dti
        
        try:
            # Get predictions using enhanced model
            prediction_results = model.predict(submitted_data)
            prediction_results.update(submitted_data)
            
            # If this is for an existing application, update it
            if app_id and application:
                application.approval_probability = prediction_results['success_probability']
                application.withdrawal_risk = prediction_results['withdrawal_risk']
                
                # Log activity
                log_activity(application.id, current_user.id, 'PREDICTION_RUN', 
                           f'ML Prediction: Approval {prediction_results["success_probability"]}%, Risk {prediction_results["withdrawal_risk"]}%')
                
                db.session.commit()
                
        except Exception as e:
            app.logger.error(f"Prediction error: {e}")
            flash(f"Error making prediction: {str(e)}", 'danger')
    
    # Get user's applications for dropdown
    user_applications = current_user.applications.filter_by(status='In-Process').all()
    
    return render_template('predictions.html', 
                         results=prediction_results, 
                         submitted_data=submitted_data,
                         user_applications=user_applications)

# Training routes
@app.route('/api/train/database', methods=['POST'])
@login_required
def train_from_database():
    """Train models using data from database"""
    if current_user.role.value != 'admin':
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    try:
        # Ensure we have a fresh database session
        with app.app_context():
            # Train model from database
            result = model.train_from_database(db.session, Application)
            
            if result['success']:
                # Log activity
                try:
                    log_activity(
                        None,  # No specific application
                        current_user.id,
                        'MODEL_TRAINING',
                        f"Models trained from database with {result.get('records_used', 0)} records"
                    )
                    db.session.commit()
                except Exception as log_error:
                    app.logger.warning(f"Could not log training activity: {log_error}")
                    # Don't fail the whole training because of logging issues
                
                return jsonify({
                    'success': True,
                    'message': result['message'],
                    'metrics': result.get('metrics'),
                    'records_used': result.get('records_used', 0)
                })
            else:
                return jsonify({
                    'success': False,
                    'message': result.get('message', 'Training failed')
                }), 400
                
    except Exception as e:
        app.logger.error(f"Training error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Training error: {str(e)}'
        }), 500

@app.route('/api/train/csv', methods=['POST'])
@login_required
def train_from_csv():
    """Train models from uploaded CSV file"""
    if current_user.role.value != 'admin':
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'success': False, 'message': 'File must be CSV format'}), 400
    
    try:
        # Save temporary file
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as tmp:
            file.save(tmp.name)
            
            try:
                # Read and validate CSV
                df = pd.read_csv(tmp.name)
                
                if len(df) == 0:
                    return jsonify({'success': False, 'message': 'CSV file is empty'}), 400
                
                # Check for required columns
                required_cols = ['Status']
                missing_cols = [col for col in required_cols if col not in df.columns]
                if missing_cols:
                    return jsonify({
                        'success': False, 
                        'message': f'Missing required columns: {", ".join(missing_cols)}'
                    }), 400
                
                # Train model
                result = model.train(df, source='csv')
                
                if result['success']:
                    # Log activity
                    try:
                        log_activity(
                            None,
                            current_user.id,
                            'MODEL_TRAINING',
                            f"Models trained from CSV with {result.get('records_used', 0)} records"
                        )
                    except Exception as log_error:
                        app.logger.warning(f"Could not log training activity: {log_error}")
                    
                    return jsonify({
                        'success': True,
                        'message': result['message'],
                        'metrics': result.get('metrics'),
                        'records_used': result.get('records_used', 0)
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': result.get('message', 'Training failed')
                    }), 400
                    
            finally:
                # Clean up temporary file
                try:
                    os.unlink(tmp.name)
                except:
                    pass
            
    except pd.errors.EmptyDataError:
        return jsonify({'success': False, 'message': 'CSV file is empty or invalid'}), 400
    except pd.errors.ParserError as e:
        return jsonify({'success': False, 'message': f'CSV parsing error: {str(e)}'}), 400
    except Exception as e:
        app.logger.error(f"CSV training error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error processing CSV: {str(e)}'
        }), 500

@app.route('/api/train/sample', methods=['POST'])
@login_required
def train_from_sample():
    """Train models from sample data"""
    if current_user.role.value != 'admin':
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    try:
        # Check if sample data exists
        sample_path = 'data/credit_data.csv'
        if not os.path.exists(sample_path):
            # Generate sample data
            try:
                from sample_data import generate_and_save_data
                generate_and_save_data(sample_path)
                app.logger.info("Generated new sample data")
            except Exception as gen_error:
                return jsonify({
                    'success': False,
                    'message': f'Error generating sample data: {str(gen_error)}'
                }), 500
        
        # Verify the file exists and is readable
        if not os.path.exists(sample_path):
            return jsonify({
                'success': False,
                'message': 'Sample data file could not be created'
            }), 500
            
        # Train from sample data
        try:
            df = pd.read_csv(sample_path)
            if len(df) == 0:
                return jsonify({
                    'success': False,
                    'message': 'Sample data file is empty'
                }), 500
                
            result = model.train(df, source='sample')
            
            if result['success']:
                # Log activity
                try:
                    log_activity(
                        None,
                        current_user.id,
                        'MODEL_TRAINING',
                        f"Models trained from sample data with {result.get('records_used', 0)} records"
                    )
                except Exception as log_error:
                    app.logger.warning(f"Could not log training activity: {log_error}")
                
                return jsonify({
                    'success': True,
                    'message': result['message'],
                    'metrics': result.get('metrics'),
                    'records_used': result.get('records_used', 0)
                })
            else:
                return jsonify({
                    'success': False,
                    'message': result.get('message', 'Training failed')
                }), 400
                
        except pd.errors.EmptyDataError:
            return jsonify({'success': False, 'message': 'Sample data file is empty or invalid'}), 500
        except pd.errors.ParserError as e:
            return jsonify({'success': False, 'message': f'Sample data parsing error: {str(e)}'}), 500
            
    except Exception as e:
        app.logger.error(f"Sample training error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error training from sample: {str(e)}'
        }), 500

@app.route('/api/model/info')
@login_required
def get_model_info():
    """Get current model information"""
    try:
        info = model.get_model_info()
        
        return jsonify({
            'success': True,
            'models_loaded': info.get('models_loaded', []),
            'metrics': info.get('last_metrics', {}),
            'feature_count': info.get('feature_count', 0),
            'history': info.get('training_history', [])
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/recalculate_predictions/<int:app_id>', methods=['POST'])
@login_required
def recalculate_predictions(app_id):
    """Manually recalculate predictions for an application"""
    try:
        application = Application.query.get_or_404(app_id)
        
        # Check permission
        if application.agent_id != current_user.id and current_user.role.value != 'admin':
            return jsonify({'success': False, 'message': 'Permission denied'}), 403
        
        # Recalculate predictions
        prediction_success, prediction_result = calculate_application_predictions(application)
        
        if prediction_success:
            db.session.commit()
            return jsonify({
                'success': True,
                'message': 'Predictions recalculated successfully',
                'approval_probability': application.approval_probability,
                'withdrawal_risk': application.withdrawal_risk
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Failed to recalculate predictions: {prediction_result}'
            }), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@app.route('/api/calculate_dti', methods=['POST'])
@login_required
def calculate_dti_api():
    """API endpoint to calculate DTI ratio from loan parameters"""
    try:
        data = request.get_json()
        
        loan_amount = float(data.get('loan_amount', 0))
        interest_rate = float(data.get('interest_rate', 0))
        loan_duration = float(data.get('loan_duration', 0))
        monthly_income = float(data.get('monthly_income', 1))
        
        dti_ratio = calculate_dti_ratio(loan_amount, interest_rate, loan_duration, monthly_income)
        
        if dti_ratio is not None:
            return jsonify({
                'success': True,
                'dti_ratio': dti_ratio,
                'dti_percentage': f"{dti_ratio:.1%}"
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid input parameters'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Calculation error: {str(e)}'
        }), 500

@app.route('/recommendations', methods=['POST'])
@login_required
def recommendations():
    """Generate strategic recommendations based on prediction results"""
    # Get form data
    submitted_data = {
        'Age': request.form.get('Age', 35, type=int),
        'Gender': request.form.get('Gender', 'Male'),
        'Credit_Score': request.form.get('Credit_Score', 650, type=int),
        'Monthly_Income': request.form.get('Monthly_Income', 35000, type=float),
        'DTI_Ratio': request.form.get('DTI_Ratio', 0.35, type=float),
        'Employment_Status': request.form.get('Employment_Status', 'Employed'),
        'Documents_Submitted': request.form.get('Documents_Submitted', 4, type=int),
        'Employment_Duration_Months': request.form.get('Employment_Duration_Months', 24, type=int),
        'Processing_Time_Days': request.form.get('days_in_process', 15, type=int),
        'completeness_score': request.form.get('completeness_score', 80, type=float),
        'Days_In_Process': request.form.get('days_in_process', 15, type=int),
        'Communication_Frequency': request.form.get('Communication_Frequency', 0.5, type=float),
        'Loan_Amount': request.form.get('Loan_Amount', 500000, type=float),
        'Property_Price': request.form.get('Property_Price', 750000, type=float),
        'Down_Payment': request.form.get('Down_Payment', 250000, type=float),
        'Interest_Rate': request.form.get('Interest_Rate', 7.5, type=float),
        'Loan_Duration': request.form.get('Loan_Duration', 20, type=int),
    }
    
    try:
        # Get predictions
        prediction_results = model.predict(submitted_data)
        
        # Generate recommendations based on results
        recs = {
            'strengths': [],
            'risks': [],
            'next_steps': []
        }
        
        # Analyze strengths
        if prediction_results['success_probability'] > 75:
            recs['strengths'].append('High approval probability indicates strong financial profile')
        if submitted_data['Credit_Score'] >= 700:
            recs['strengths'].append(f"Excellent credit score of {submitted_data['Credit_Score']}")
        if submitted_data['DTI_Ratio'] < 0.36:
            recs['strengths'].append(f"Healthy debt-to-income ratio at {submitted_data['DTI_Ratio']:.1%}")
        if prediction_results['completeness_score'] >= 80:
            recs['strengths'].append(f"Strong document completeness at {prediction_results['completeness_score']}%")
        if submitted_data['Monthly_Income'] > 40000:
            recs['strengths'].append(f"Strong monthly income of Q{submitted_data['Monthly_Income']:,.0f}")
        
        # Calculate LTV
        ltv = (submitted_data['Loan_Amount'] / submitted_data['Property_Price']) * 100 if submitted_data['Property_Price'] > 0 else 0
        if ltv < 80:
            recs['strengths'].append(f"Conservative loan-to-value ratio at {ltv:.1f}%")
        
        # Analyze risks
        if prediction_results['withdrawal_risk'] > 50:
            recs['risks'].append({
                'text': f"Elevated withdrawal risk at {prediction_results['withdrawal_risk']}% requires immediate attention",
                'priority': 'High'
            })
        if submitted_data['Credit_Score'] < 650:
            recs['risks'].append({
                'text': f"Credit score of {submitted_data['Credit_Score']} may impact approval chances",
                'priority': 'High'
            })
        if submitted_data['DTI_Ratio'] > 0.43:
            recs['risks'].append({
                'text': f"High debt-to-income ratio at {submitted_data['DTI_Ratio']:.1%} exceeds recommended threshold",
                'priority': 'Medium'
            })
        if prediction_results['completeness_score'] < 60:
            recs['risks'].append({
                'text': f"Low document completeness at {prediction_results['completeness_score']}% delays processing",
                'priority': 'High'
            })
        if submitted_data['Days_In_Process'] > 30:
            recs['risks'].append({
                'text': f"Extended processing time of {submitted_data['Days_In_Process']} days increases withdrawal risk",
                'priority': 'Medium'
            })
        if ltv > 90:
            recs['risks'].append({
                'text': f"High LTV ratio at {ltv:.1f}% may require additional collateral",
                'priority': 'Medium'
            })
        
        # Generate next steps
        if prediction_results['withdrawal_risk'] > 65:
            recs['next_steps'].append({
                'icon': 'bi-telephone-fill',
                'text': 'Contact applicant within 24 hours to address concerns'
            })
            recs['next_steps'].append({
                'icon': 'bi-person-check-fill',
                'text': 'Assign dedicated relationship manager'
            })
        
        if prediction_results['completeness_score'] < 100:
            recs['next_steps'].append({
                'icon': 'bi-file-earmark-check',
                'text': f"Collect remaining {5 - submitted_data['Documents_Submitted']} documents"
            })
        
        if prediction_results['success_probability'] < 50:
            recs['next_steps'].append({
                'icon': 'bi-calculator',
                'text': 'Review financial requirements with applicant'
            })
            recs['next_steps'].append({
                'icon': 'bi-cash-stack',
                'text': 'Consider alternative financing options'
            })
        else:
            recs['next_steps'].append({
                'icon': 'bi-speedometer2',
                'text': 'Fast-track application for underwriting review'
            })
        
        if submitted_data['Communication_Frequency'] < 1:
            recs['next_steps'].append({
                'icon': 'bi-calendar-check',
                'text': 'Schedule weekly progress updates with applicant'
            })
        
        # Always add final step
        recs['next_steps'].append({
            'icon': 'bi-graph-up-arrow',
            'text': 'Monitor application progress daily until decision'
        })
        
        return render_template('recommendations.html', recs=recs)
        
    except Exception as e:
        app.logger.error(f"Recommendation generation error: {e}")
        return f"<p class='text-danger'>Error generating recommendations: {str(e)}</p>", 500

@app.route('/withdrawal', methods=['GET', 'POST'])
@login_required
def withdrawal():
    """Withdrawal risk assessment page"""
    results = None
    if request.method == 'POST':
        input_data = {
            'Credit_Score': request.form.get('credit_score', default=0, type=int),
            'Documents_Submitted': request.form.get('docs_submitted_count', default=0, type=int),
            'Employment_Duration_Months': request.form.get('employment_length_months', default=0, type=int),
            'Days_In_Process': request.form.get('days_in_process', default=0, type=int),
            'Communication_Frequency': request.form.get('comm_frequency', default=0.0, type=float),
            'Loan_Amount': request.form.get('loan_amount', default=500000, type=float),
            'Property_Price': request.form.get('property_price', default=750000, type=float),
            'Down_Payment': request.form.get('property_price', default=750000, type=float) - request.form.get('loan_amount', default=500000, type=float),
            'Monthly_Income': request.form.get('monthly_income', default=35000, type=float),
            'Interest_Rate': request.form.get('interest_rate', default=7.5, type=float),
            'Loan_Duration': request.form.get('loan_duration', default=20, type=int),
        }
        
        risk_decimal = model.predict_withdrawal_rule_based(input_data)
        risk_percentage = round(risk_decimal * 100, 1)
        risk_percentage = max(0, min(100, risk_percentage))
        
        # Calculate needle position for the gauge
        import math
        angle_degrees = risk_percentage * 1.8  # 180 degrees for 0-100%
        angle_radians = math.radians(angle_degrees)
        needle_x = 160 - (85 * math.cos(angle_radians))
        needle_y = 170 - (85 * math.sin(angle_radians))
        
        results = {
            'risk_score': risk_percentage,
            'needle_x': needle_x,
            'needle_y': needle_y
        }
    
    return render_template('withdrawal_prediction.html', results=results)

@app.route('/completeness', methods=['GET', 'POST'])
@login_required
def completeness():
    """Document completeness assessment"""
    lang = session.get('language', 'en')
    results = None
    
    if request.method == 'POST':
        submitted_docs = request.form.getlist('documents')
        applicant_id = request.form.get('applicant_id', '').strip()
        
        if not applicant_id:
            flash(_get_text(lang, 'applicant_id_required'), 'warning')
            return render_template('completeness.html', required_docs=REQUIRED_DOCS, results=None)
        
        # Calculate weighted completeness
        DOCUMENT_WEIGHTS = {
            'critical': {
                'weight': 0.6,
                'docs': ['doc_id', 'doc_salary', 'doc_bank_statement']
            },
            'supplementary': {
                'weight': 0.4,
                'docs': ['doc_tax_return', 'doc_property_docs']
            }
        }
        
        critical_docs = DOCUMENT_WEIGHTS['critical']['docs']
        supplementary_docs = DOCUMENT_WEIGHTS['supplementary']['docs']
        
        critical_submitted = sum(1 for doc in critical_docs if doc in submitted_docs)
        critical_score = critical_submitted / len(critical_docs) if critical_docs else 0
        
        supplementary_submitted = sum(1 for doc in supplementary_docs if doc in submitted_docs)
        supplementary_score = supplementary_submitted / len(supplementary_docs) if supplementary_docs else 0
        
        final_score = (critical_score * DOCUMENT_WEIGHTS['critical']['weight']) + \
                     (supplementary_score * DOCUMENT_WEIGHTS['supplementary']['weight'])
        
        score = round(final_score * 100, 1)
        
        # Determine status
        if score == 100:
            status = _get_text(lang, 'status_complete')
        elif score >= 60:
            status = _get_text(lang, 'status_ready_for_review')
        else:
            status = _get_text(lang, 'status_incomplete')
        
        # Get missing documents
        missing_docs_detailed = []
        missing_critical = [doc for doc in critical_docs if doc not in submitted_docs]
        missing_supplementary = [doc for doc in supplementary_docs if doc not in submitted_docs]
        
        for doc in missing_critical:
            missing_docs_detailed.append({
                'doc': _get_text(lang, doc),
                'priority': 'High',
                'type': 'Critical'
            })
        
        for doc in missing_supplementary:
            missing_docs_detailed.append({
                'doc': _get_text(lang, doc),
                'priority': 'Medium',
                'type': 'Supplementary'
            })
        
        results = {
            'score': score,
            'status': status,
            'missing_docs_detailed': missing_docs_detailed,
            'applicant_id': applicant_id,
            'critical_percentage': round((critical_submitted / len(critical_docs)) * 100, 1) if critical_docs else 0,
            'supplementary_percentage': round((supplementary_submitted / len(supplementary_docs)) * 100, 1) if supplementary_docs else 0,
            'critical_submitted': critical_submitted,
            'critical_total': len(critical_docs),
            'supplementary_submitted': supplementary_submitted,
            'supplementary_total': len(supplementary_docs),
            'document_weights': DOCUMENT_WEIGHTS,
            'submitted_docs': submitted_docs  # Add this for form state preservation
        }
    
    return render_template('completeness.html', 
                         required_docs=REQUIRED_DOCS, 
                         results=results,
                         document_weights={'critical': {'docs': ['doc_id', 'doc_salary', 'doc_bank_statement']},
                                         'supplementary': {'docs': ['doc_tax_return', 'doc_property_docs']}})

@app.route('/api/applications/recent')
@login_required
def api_recent_applications():
    """API endpoint for recent applications"""
    limit = request.args.get('limit', 10, type=int)
    
    if current_user.role.value == 'admin':
        applications = Application.query.order_by(Application.application_date.desc()).limit(limit).all()
    else:
        applications = current_user.applications.order_by(Application.application_date.desc()).limit(limit).all()
    
    return jsonify([app.to_dict() for app in applications])

@app.route('/api/applications/stats')
@login_required
def api_application_stats():
    """API endpoint for application statistics"""
    if current_user.role.value == 'admin':
        total = Application.query.count()
        in_process = Application.query.filter_by(status='In-Process').count()
        approved = Application.query.filter_by(status='Approved').count()
        declined = Application.query.filter_by(status='Declined').count()
        withdrawn = Application.query.filter_by(status='Withdrawn').count()
    else:
        total = current_user.applications.count()
        in_process = current_user.applications.filter_by(status='In-Process').count()
        approved = current_user.applications.filter_by(status='Approved').count()
        declined = current_user.applications.filter_by(status='Declined').count()
        withdrawn = current_user.applications.filter_by(status='Withdrawn').count()
    
    return jsonify({
        'total': total,
        'in_process': in_process,
        'approved': approved,
        'declined': declined,
        'withdrawn': withdrawn,
        'approval_rate': round((approved / total * 100) if total > 0 else 0, 1)
    })

# Custom Jinja2 filters for math operations
@app.template_filter('cos')
def cos_filter(value):
    """Cosine filter for Jinja2 templates"""
    import math
    return math.cos(value)

@app.template_filter('sin')
def sin_filter(value):
    """Sine filter for Jinja2 templates"""
    import math
    return math.sin(value)

@app.template_filter('radians')
def radians_filter(value):
    """Convert degrees to radians"""
    import math
    return math.radians(value)

@app.template_filter('round')
def round_filter(value, precision=0):
    """Round a number to specified precision"""
    return round(value, precision)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4446, debug=True)