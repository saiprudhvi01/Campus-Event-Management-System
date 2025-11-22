from app import app, db, Club, Student, Event, Registration
from werkzeug.security import generate_password_hash

def initialize_database():
    with app.app_context():
        # Drop all tables and recreate them
        db.drop_all()
        db.create_all()
        
        # Create initial clubs
        clubs = ['Club A', 'Club B', 'Club C', 'Club D', 'Club E']
        for club_name in clubs:
            club = Club(club_name=club_name, password='1234')
            db.session.add(club)
        
        # Create sample students
        students_data = [
            {'name': 'John Doe', 'reg_no': 'REG001', 'email': 'john@campus.edu'},
            {'name': 'Jane Smith', 'reg_no': 'REG002', 'email': 'jane@campus.edu'},
            {'name': 'Mike Johnson', 'reg_no': 'REG003', 'email': 'mike@campus.edu'},
        ]
        
        for student_data in students_data:
            student = Student(
                name=student_data['name'],
                reg_no=student_data['reg_no'],
                email=student_data['email']
            )
            student.set_password('password123')
            db.session.add(student)
        
        db.session.commit()
        
        # Create sample events
        club_a = Club.query.filter_by(club_name='Club A').first()
        club_b = Club.query.filter_by(club_name='Club B').first()
        
        if club_a:
            event1 = Event(
                club_id=club_a.id,
                event_name='Tech Workshop',
                description='Learn the latest technologies and programming frameworks',
                credits=5
            )
            db.session.add(event1)
        
        if club_b:
            event2 = Event(
                club_id=club_b.id,
                event_name='Cultural Festival',
                description='Annual cultural festival with music, dance, and drama performances',
                credits=3
            )
            db.session.add(event2)
        
        db.session.commit()
        
        # Create sample registrations
        student1 = Student.query.filter_by(reg_no='REG001').first()
        student2 = Student.query.filter_by(reg_no='REG002').first()
        
        if student1 and event1:
            reg1 = Registration(student_id=student1.id, event_id=event1.id, status='Pending')
            db.session.add(reg1)
        
        if student2 and event1:
            reg2 = Registration(student_id=student2.id, event_id=event1.id, status='Accepted')
            db.session.add(reg2)
        
        db.session.commit()
        
        print("Database initialized successfully!")
        print("Created clubs: Club A, Club B, Club C, Club D, Club E")
        print("Sample students: REG001, REG002, REG003 (password: password123)")
        print("Sample events created")
        print("Sample registrations created")

if __name__ == '__main__':
    initialize_database()
