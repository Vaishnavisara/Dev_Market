import os
import logging
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager, current_user, login_required
from werkzeug.security import check_password_hash

from dotenv import load_dotenv
load_dotenv()

# This should be at the beginning of your file, before your app configuration

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Setup base database class
class Base(DeclarativeBase):
    pass

# Initialize Flask extensions
db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# Configure the database - use SQLite for MVP
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///marketplace.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize database with app
db.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

with app.app_context():
    # Import models here for database creation
    from models import User, Project, Message, Company, Payment
    db.create_all()

# Import user loader function and auth blueprint from google_auth.py
from models import User
from google_auth import google_auth

# Register blueprints
app.register_blueprint(google_auth)

# Import payment blueprint
from payment import payment_bp
app.register_blueprint(payment_bp)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Import forms
from forms import LoginForm, RegistrationForm, ProjectForm, CompanyProfileForm, MessageForm

# Routes
@app.route('/')
def index():
    """Home page with featured projects and companies"""
    projects = Project.query.order_by(Project.created_at.desc()).limit(6).all()
    companies = Company.query.limit(4).all()
    return render_template('index.html', projects=projects, companies=companies)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Traditional login page with email/password"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            from flask_login import login_user
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        from werkzeug.security import generate_password_hash
        from models import User
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('An account with that email already exists', 'danger')
            return render_template('register.html', form=form)
        
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            user_type=form.user_type.data
        )
        
        db.session.add(user)
        db.session.commit()
        
        # If user is a company, create company profile
        if form.user_type.data == 'company':
            company = Company(user_id=user.id, name=form.username.data)
            db.session.add(company)
            db.session.commit()
        
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    """Log out the current user"""
    from flask_login import logout_user
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/projects')
def projects():
    """Display all available projects"""
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('projects.html', projects=projects)

@app.route('/projects/<int:project_id>')
def project_detail(project_id):
    """Display details of a specific project"""
    project = Project.query.get_or_404(project_id)
    return render_template('project_detail.html', project=project)

@app.route('/create_project', methods=['GET', 'POST'])
@login_required
def create_project():
    """Create a new project (client only)"""
    if current_user.user_type != 'client':
        flash('Only clients can post projects', 'danger')
        return redirect(url_for('index'))
    
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(
            title=form.title.data,
            description=form.description.data,
            budget=form.budget.data,
            client_id=current_user.id,
            status='open'
        )
        db.session.add(project)
        db.session.commit()
        flash('Your project has been posted!', 'success')
        return redirect(url_for('projects'))
    
    return render_template('create_project.html', form=form)

@app.route('/company/<int:company_id>')
def company_profile(company_id):
    """Display company profile and portfolio"""
    company = Company.query.get_or_404(company_id)
    return render_template('company_profile.html', company=company)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile (both client and company)"""
    form = CompanyProfileForm()
    
    # If user is a company, load company profile
    company = None
    if current_user.user_type == 'company':
        company = Company.query.filter_by(user_id=current_user.id).first()
        
    if form.validate_on_submit():
        if company:
            company.name = form.name.data
            company.description = form.description.data
            company.website = form.website.data
            company.services = form.services.data
            db.session.commit()
            flash('Your company profile has been updated!', 'success')
        return redirect(url_for('index'))
    
    # Pre-populate form if editing
    if company and request.method == 'GET':
        form.name.data = company.name
        form.description.data = company.description
        form.website.data = company.website
        form.services.data = company.services
    
    return render_template('edit_profile.html', form=form)

@app.route('/messages')
@login_required
def messages():
    """Display user messages"""
    received_messages = Message.query.filter_by(recipient_id=current_user.id).order_by(Message.timestamp.desc()).all()
    sent_messages = Message.query.filter_by(sender_id=current_user.id).order_by(Message.timestamp.desc()).all()
    form = MessageForm()
    return render_template('messages.html', received_messages=received_messages, sent_messages=sent_messages, form=form)

@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    """Send a message to another user"""
    form = MessageForm()
    if form.validate_on_submit():
        recipient = User.query.filter_by(username=form.recipient.data).first()
        if not recipient:
            flash('User not found', 'danger')
            return redirect(url_for('messages'))
        
        message = Message(
            sender_id=current_user.id,
            recipient_id=recipient.id,
            content=form.content.data
        )
        db.session.add(message)
        db.session.commit()
        flash('Message sent!', 'success')
    
    return redirect(url_for('messages'))

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return render_template('500.html'), 500


@app.route('/companies')
def company_list():
    """Display a list of all registered companies"""
    companies = Company.query.all()
    return render_template('company_list.html', companies=companies)