import os
import stripe
from flask import Blueprint, redirect, request, url_for, render_template, flash, jsonify
from flask_login import login_required, current_user
from app import db
from models import Payment, Project

# Set up Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', '')

YOUR_DOMAIN = os.environ.get('REPLIT_DEV_DOMAIN', 'localhost:5000')
if not YOUR_DOMAIN.startswith('http'):
    YOUR_DOMAIN = 'https://' + YOUR_DOMAIN

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/payment/<int:project_id>', methods=['GET'])
@login_required
def payment_page(project_id):
    """Show payment page for a project"""
    project = Project.query.get_or_404(project_id)
    
    # Check if user is authorized to pay for this project
    if current_user.id != project.client_id:
        flash('You are not authorized to make payment for this project', 'danger')
        return redirect(url_for('project_detail', project_id=project_id))
    
    return render_template('payment.html', project=project)

@payment_bp.route('/create-checkout-session/<int:project_id>', methods=['POST'])
@login_required
def create_checkout_session(project_id):
    """Create a Stripe checkout session for a project payment"""
    if not stripe.api_key:
        flash('Stripe is not configured', 'danger')
        return redirect(url_for('payment_page', project_id=project_id))
    
    project = Project.query.get_or_404(project_id)
    
    # Check if user is authorized to pay for this project
    if current_user.id != project.client_id:
        flash('You are not authorized to make payment for this project', 'danger')
        return redirect(url_for('project_detail', project_id=project_id))
    
    try:
        # Create a new payment record
        payment = Payment(
            amount=project.budget,
            status='pending',
            user_id=current_user.id,
            project_id=project_id
        )
        db.session.add(payment)
        db.session.commit()
        
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f'Payment for project: {project.title}',
                        },
                        'unit_amount': int(project.budget * 100),  # Convert to cents
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=YOUR_DOMAIN + f'/payment/success/{payment.id}',
            cancel_url=YOUR_DOMAIN + f'/payment/cancel/{payment.id}',
        )
        
        # Update payment with Stripe ID
        payment.stripe_payment_id = checkout_session.id
        db.session.commit()
        
        return redirect(checkout_session.url, code=303)
    
    except Exception as e:
        flash(f'Payment error: {str(e)}', 'danger')
        return redirect(url_for('payment_page', project_id=project_id))

@payment_bp.route('/payment/success/<int:payment_id>')
@login_required
def payment_success(payment_id):
    """Payment success page"""
    payment = Payment.query.get_or_404(payment_id)
    
    # Update payment status
    payment.status = 'completed'
    payment.completed_at = db.func.now()
    
    # Update project status
    project = Project.query.get(payment.project_id)
    if project:
        project.status = 'in_progress'
    
    db.session.commit()
    
    return render_template('payment_success.html', payment=payment, project=project)

@payment_bp.route('/payment/cancel/<int:payment_id>')
@login_required
def payment_cancel(payment_id):
    """Payment cancel page"""
    payment = Payment.query.get_or_404(payment_id)
    
    # Update payment status
    payment.status = 'failed'
    db.session.commit()
    
    return render_template('payment_cancel.html', payment=payment)

@payment_bp.route('/webhook', methods=['POST'])
def webhook():
    """Stripe webhook for payment events"""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    if not stripe.api_key:
        return jsonify({'status': 'error', 'message': 'Stripe not configured'}), 400
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ.get('STRIPE_WEBHOOK_SECRET', '')
        )
        
        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            
            # Find the payment
            payment = Payment.query.filter_by(stripe_payment_id=session.id).first()
            if payment:
                payment.status = 'completed'
                payment.completed_at = db.func.now()
                
                # Update the project status
                project = Project.query.get(payment.project_id)
                if project:
                    project.status = 'in_progress'
                
                db.session.commit()
        
        return jsonify({'status': 'success'})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
