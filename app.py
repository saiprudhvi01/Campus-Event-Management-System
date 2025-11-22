from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from models import db, Club, Student, Event, Registration
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import re
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def init_database():
    with app.app_context():
        db.create_all()
        
        # Create initial clubs if they don't exist
        clubs = ['Club A', 'Club B', 'Club C', 'Club D', 'Club E']
        for club_name in clubs:
            existing_club = Club.query.filter_by(club_name=club_name).first()
            if not existing_club:
                club = Club(club_name=club_name, password='1234')
                db.session.add(club)
        
        db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

# Club Routes
@app.route('/club_login', methods=['GET', 'POST'])
def club_login():
    if request.method == 'POST':
        club_name = request.form['club_name']
        password = request.form['password']
        
        club = Club.query.filter_by(club_name=club_name, password=password).first()
        if club:
            session['club_id'] = club.id
            session['club_name'] = club.club_name
            session['user_type'] = 'club'
            flash('Login successful!', 'success')
            return redirect(url_for('club_dashboard'))
        else:
            flash('Invalid club name or password', 'error')
    
    return render_template('club_login.html')

@app.route('/club_dashboard')
def club_dashboard():
    if 'club_id' not in session or session.get('user_type') != 'club':
        return redirect(url_for('club_login'))
    
    club = Club.query.get(session['club_id'])
    events = Event.query.filter_by(club_id=session['club_id']).all()
    
    # Get registrations for each event
    event_registrations = {}
    for event in events:
        registrations = Registration.query.filter_by(event_id=event.id).all()
        event_registrations[event.id] = registrations
    
    return render_template('club_dashboard.html', club=club, events=events, event_registrations=event_registrations)

@app.route('/create_event', methods=['GET', 'POST'])
def create_event():
    if 'club_id' not in session or session.get('user_type') != 'club':
        return redirect(url_for('club_login'))
    
    if request.method == 'POST':
        event_name = request.form['event_name']
        description = request.form['description']
        credits = request.form['credits']
        
        if not event_name or not description or not credits:
            flash('All fields are required!', 'error')
        else:
            event = Event(
                club_id=session['club_id'],
                event_name=event_name,
                description=description,
                credits=int(credits)
            )
            db.session.add(event)
            db.session.commit()
            flash('Event created successfully!', 'success')
            return redirect(url_for('club_dashboard'))
    
    return render_template('create_event.html')

@app.route('/update_registration/<int:registration_id>/<string:status>')
def update_registration(registration_id, status):
    if 'club_id' not in session or session.get('user_type') != 'club':
        return redirect(url_for('club_login'))
    
    registration = Registration.query.get_or_404(registration_id)
    event = Event.query.get(registration.event_id)
    
    if event.club_id != session['club_id']:
        flash('Unauthorized action!', 'error')
        return redirect(url_for('club_dashboard'))
    
    if status in ['Accepted', 'Rejected']:
        registration.status = status
        db.session.commit()
        flash(f'Registration {status} successfully!', 'success')
    
    return redirect(url_for('club_dashboard'))

# Student Routes
@app.route('/student_login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        reg_no = request.form['reg_no']
        password = request.form['password']
        
        student = Student.query.filter_by(reg_no=reg_no).first()
        if student and student.check_password(password):
            session['student_id'] = student.id
            session['student_name'] = student.name
            session['user_type'] = 'student'
            flash('Login successful!', 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid register number or password', 'error')
    
    return render_template('student_login.html')

@app.route('/student_register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        name = request.form['name']
        reg_no = request.form['reg_no']
        email = request.form['email']
        password = request.form['password']
        
        if not name or not reg_no or not email or not password:
            flash('All fields are required!', 'error')
        elif Student.query.filter_by(reg_no=reg_no).first():
            flash('Register number already exists!', 'error')
        elif Student.query.filter_by(email=email).first():
            flash('Email already exists!', 'error')
        else:
            student = Student(name=name, reg_no=reg_no, email=email)
            student.set_password(password)
            db.session.add(student)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('student_login'))
    
    return render_template('student_register.html')

@app.route('/student_dashboard')
def student_dashboard():
    if 'student_id' not in session or session.get('user_type') != 'student':
        return redirect(url_for('student_login'))
    
    student = Student.query.get(session['student_id'])
    events = Event.query.all()
    
    # Get student's registrations
    student_registrations = {}
    for registration in student.registrations:
        student_registrations[registration.event_id] = registration.status
    
    return render_template('student_dashboard.html', student=student, events=events, student_registrations=student_registrations)

@app.route('/register_event/<int:event_id>', methods=['GET', 'POST'])
def register_event(event_id):
    if 'student_id' not in session or session.get('user_type') != 'student':
        return redirect(url_for('student_login'))
    
    event = Event.query.get_or_404(event_id)
    student_id = session['student_id']
    
    # Check if already registered
    existing_registration = Registration.query.filter_by(student_id=student_id, event_id=event_id).first()
    if existing_registration:
        flash('You have already registered for this event!', 'error')
        return redirect(url_for('student_dashboard'))
    
    if request.method == 'POST':
        registration = Registration(student_id=student_id, event_id=event_id, status='Pending')
        db.session.add(registration)
        db.session.commit()
        flash('Event registration submitted successfully!', 'success')
        return redirect(url_for('student_dashboard'))
    
    return render_template('register_event.html', event=event)

# Admin Routes
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == 'admin' and password == 'admin123':
            session['admin_id'] = 1
            session['admin_name'] = 'admin'
            session['user_type'] = 'admin'
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_id' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('admin_login'))
    
    clubs = Club.query.all()
    events = Event.query.all()
    registrations = Registration.query.all()
    
    return render_template('admin_dashboard.html', clubs=clubs, events=events, registrations=registrations)

@app.route('/add_club', methods=['GET', 'POST'])
def add_club():
    if 'admin_id' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        club_name = request.form['club_name']
        password = request.form['password']
        
        if not club_name or not password:
            flash('All fields are required!', 'error')
        elif Club.query.filter_by(club_name=club_name).first():
            flash('Club already exists!', 'error')
        else:
            club = Club(club_name=club_name, password=password)
            db.session.add(club)
            db.session.commit()
            flash('Club added successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
    
    return render_template('add_club.html')

@app.route('/delete_club/<int:club_id>')
def delete_club(club_id):
    if 'admin_id' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('admin_login'))
    
    club = Club.query.get_or_404(club_id)
    
    # Delete related events and registrations
    events = Event.query.filter_by(club_id=club_id).all()
    for event in events:
        Registration.query.filter_by(event_id=event.id).delete()
    
    Event.query.filter_by(club_id=club_id).delete()
    db.session.delete(club)
    db.session.commit()
    
    flash('Club deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

# Chatbot Routes
@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/chatbot_process', methods=['POST'])
def chatbot_process():
    try:
        data = request.get_json()
        user_message = data.get('message', '').lower().strip()
        
        if not user_message:
            return jsonify({'response': 'Please ask me something about clubs, events, or registrations!'})
        
        # Process the query using NLP logic
        response = process_chatbot_query(user_message)
        
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'response': 'Sorry, I encountered an error. Please try again.'})

def process_chatbot_query(message):
    """Main NLP processing function for chatbot queries"""
    
    # Sanitize input
    message = re.sub(r'[^\w\s\?\!\.\,\-]', '', message)
    
    # Club Information Queries
    if any(keyword in message for keyword in ['club', 'clubs', 'available', 'list']):
        if any(keyword in message for keyword in ['what', 'show', 'list', 'available']):
            return get_clubs_information()
    
    # Event Information Queries
    if any(keyword in message for keyword in ['event', 'events', 'show', 'what']):
        # Check for credit filtering
        credit_match = re.search(r'(\d+)\s*credit', message)
        if credit_match:
            credits = int(credit_match.group(1))
            return get_events_by_credits(credits)
        
        # Check for club-specific events
        club_match = re.search(r'club\s+([a-e])', message, re.IGNORECASE)
        if club_match:
            club_letter = club_match.group(1).upper()
            club_name = f"Club {club_letter}"
            return get_events_by_club(club_name)
        
        # General events query
        if any(keyword in message for keyword in ['what', 'show', 'list', 'available', 'all']):
            return get_all_events()
    
    # Registration Process Queries
    if any(keyword in message for keyword in ['register', 'registration', 'sign up', 'how to', 'process']):
        return get_registration_help()
    
    # Recommendation Queries
    if any(keyword in message for keyword in ['recommend', 'best', 'suggest', 'good']):
        return get_event_recommendations(message)
    
    # Fallback response
    return get_fallback_response()

def get_clubs_information():
    """Get information about all available clubs"""
    try:
        clubs = Club.query.all()
        if not clubs:
            return "No clubs are currently available in the system."
        
        response = "🏢 **Available Clubs:**\n\n"
        for club in clubs:
            event_count = Event.query.filter_by(club_id=club.id).count()
            response += f"• **{club.club_name}** - {event_count} event(s)\n"
        
        response += f"\nTotal: {len(clubs)} clubs available"
        return response
    except Exception as e:
        return "Sorry, I couldn't retrieve club information right now."

def get_all_events():
    """Get information about all events"""
    try:
        events = Event.query.all()
        if not events:
            return "No events are currently available."
        
        response = "🎪 **All Available Events:**\n\n"
        for event in events:
            response += f"• **{event.event_name}**\n"
            response += f"  📝 {event.description}\n"
            response += f"  💳 {event.credits} credits\n"
            response += f"  🏢 by {event.club.club_name}\n\n"
        
        response += f"Total: {len(events)} events available"
        return response
    except Exception as e:
        return "Sorry, I couldn't retrieve event information right now."

def get_events_by_credits(credits):
    """Get events filtered by credit value"""
    try:
        events = Event.query.filter_by(credits=credits).all()
        if not events:
            return f"No events found that offer {credits} credits."
        
        response = f"💳 **Events with {credits} credits:**\n\n"
        for event in events:
            response += f"• **{event.event_name}**\n"
            response += f"  📝 {event.description}\n"
            response += f"  🏢 by {event.club.club_name}\n\n"
        
        response += f"Found: {len(events)} event(s) with {credits} credits"
        return response
    except Exception as e:
        return f"Sorry, I couldn't search for events with {credits} credits."

def get_events_by_club(club_name):
    """Get events conducted by a specific club"""
    try:
        club = Club.query.filter_by(club_name=club_name).first()
        if not club:
            return f"Club '{club_name}' not found."
        
        events = Event.query.filter_by(club_id=club.id).all()
        if not events:
            return f"{club_name} hasn't created any events yet."
        
        response = f"🏢 **Events by {club_name}:**\n\n"
        for event in events:
            response += f"• **{event.event_name}**\n"
            response += f"  📝 {event.description}\n"
            response += f"  💳 {event.credits} credits\n\n"
        
        response += f"Total: {len(events)} event(s) by {club_name}"
        return response
    except Exception as e:
        return f"Sorry, I couldn't retrieve events for {club_name}."

def get_registration_help():
    """Get help information about the registration process"""
    response = "📝 **How to Register for Events:**\n\n"
    response += "1. **Create Student Account:**\n"
    response += "   • Go to Student Login\n"
    response += "   • Click 'Register here'\n"
    response += "   • Fill in your details (name, reg no, email, password)\n\n"
    response += "2. **Login to Your Account:**\n"
    response += "   • Use your register number and password\n\n"
    response += "3. **Browse Events:**\n"
    response += "   • View all available events on your dashboard\n"
    response += "   • See event details, credits, and organizing clubs\n\n"
    response += "4. **Register for Events:**\n"
    response += "   • Click 'Register for Event' button\n"
    response += "   • Submit the registration form\n"
    response += "   • Wait for club approval (Pending → Accepted/Rejected)\n\n"
    response += "5. **Track Your Status:**\n"
    response += "   • Check your dashboard for registration status\n"
    response += "   • Accepted registrations are confirmed\n\n"
    response += "💡 **Tip:** Register early as clubs may have limited capacity!"
    return response

def get_event_recommendations(message):
    """Get event recommendations based on user preferences"""
    # Check for credit preference
    credit_match = re.search(r'(\d+)\s*credit', message)
    if credit_match:
        credits = int(credit_match.group(1))
        events = Event.query.filter(Event.credits >= credits).order_by(Event.credits.desc()).limit(3).all()
    else:
        # Recommend events with most credits
        events = Event.query.order_by(Event.credits.desc()).limit(3).all()
    
    if not events:
        return "No events available for recommendation at the moment."
    
    response = "⭐ **Event Recommendations:**\n\n"
    for i, event in enumerate(events, 1):
        response += f"{i}. **{event.event_name}**\n"
        response += f"   📝 {event.description}\n"
        response += f"   💳 {event.credits} credits\n"
        response += f"   🏢 by {event.club.club_name}\n\n"
    
    response += "💡 **Recommendation Tip:** Consider events that match your interests and credit requirements!"
    return response

def get_fallback_response():
    """Fallback response for unrecognized queries"""
    responses = [
        "I can help you with information about clubs, events, and registrations. Try asking about available clubs or events!",
        "I'm here to assist with event-related questions. Ask me about clubs, events, credits, or the registration process.",
        "I can provide information about available clubs, events, and how to register. What would you like to know?",
        "Try asking me: 'What clubs are available?' or 'Show me all events' or 'How do I register for an event?'"
    ]
    import random
    return random.choice(responses)

if __name__ == '__main__':
    init_database()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
