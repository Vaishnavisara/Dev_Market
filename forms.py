from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, FloatField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    user_type = SelectField('I am a', choices=[('client', 'Client'), ('company', 'Company')], validators=[DataRequired()])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please use a different one.')

class ProjectForm(FlaskForm):
    title = StringField('Project Title', validators=[DataRequired(), Length(min=5, max=100)])
    description = TextAreaField('Project Description', validators=[DataRequired(), Length(min=20)])
    budget = FloatField('Budget (USD)', validators=[DataRequired()])
    submit = SubmitField('Post Project')

class CompanyProfileForm(FlaskForm):
    name = StringField('Company Name', validators=[DataRequired(), Length(min=3, max=100)])
    description = TextAreaField('Company Description', validators=[DataRequired(), Length(min=20)])
    website = StringField('Website', validators=[Length(max=120)])
    services = TextAreaField('Services Offered', validators=[DataRequired()])
    submit = SubmitField('Update Profile')

class MessageForm(FlaskForm):
    recipient = StringField('To Username', validators=[DataRequired()])
    content = TextAreaField('Message', validators=[DataRequired(), Length(min=1, max=1000)])
    submit = SubmitField('Send Message')
