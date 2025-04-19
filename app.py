from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, Event, Registration
from db_config import get_connection  # Still assuming you use raw SQL for some parts

app = Flask(__name__)
app.secret_key = 'flask_event_project_2025_secret_key'  # required for session/flash

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Dummy admin credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password123'

with app.app_context():
    db.create_all()

    if not Event.query.first():
        sample_event = Event(name="Hackathon 2025", date="2025-05-10", location="Virtual")
        db.session.add(sample_event)
        db.session.commit()


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/events')
def show_events():
    events = Event.query.all()
    return render_template("events.html", events=events)


@app.route('/register', methods=['GET', 'POST'])
def register():
    events = Event.query.all()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        event_id = request.form['event_id']

        if name and email and event_id:
            registration = Registration(name=name, email=email, event_id=event_id)
            db.session.add(registration)
            db.session.commit()
            return redirect(url_for('home'))
        else:
            return "Please fill out all fields", 400

    return render_template('register.html', events=events)


@app.route('/registrations')
def registrations():
    all_registrations = Registration.query.join(Event, Registration.event_id == Event.id).add_columns(
        Registration.name, Registration.email, Event.name.label("event_name")
    ).all()
    
    return render_template("registrations.html", data=all_registrations)


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash("Logged in successfully!")
            return redirect(url_for('admin'))
        else:
            flash("Invalid credentials!", "error")
    return render_template("admin_login.html")


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash("Logged out.")
    return redirect(url_for('home'))


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        name = request.form['name']
        date = request.form['date']
        location = request.form['location']
        
        if name and date and location:
            new_event = Event(name=name, date=date, location=location)
            db.session.add(new_event)
            db.session.commit()
            flash('Event added successfully!')
            return redirect(url_for('admin'))
        else:
            flash('Please fill out all fields.')

    events = Event.query.all()
    return render_template('admin.html', events=events)


@app.route('/delete_event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    event = Event.query.get(event_id)
    if event:
        db.session.delete(event)
        db.session.commit()
        flash('Event deleted successfully!')
    else:
        flash('Event not found.')
    return redirect(url_for('admin'))


if __name__ == '__main__':
    app.run(debug=True)
