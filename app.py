# backend/app.py
from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import threading, time, logging
from notifications import send_push_notification  # Ensure this file exists with the function

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("JRPrayerReminder")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reminders.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the Reminder model
class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(80), nullable=False)
    time_str = db.Column(db.String(5), nullable=False)  # Format "HH:MM"
    scripture = db.Column(db.String(200), nullable=True)
    last_triggered_date = db.Column(db.Date, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user": self.user,
            "time": self.time_str,
            "scripture": self.scripture,
            "last_triggered_date": self.last_triggered_date.isoformat() if self.last_triggered_date else None
        }

# Create the database tables if they don't exist
with app.app_context():
    db.create_all()

# Define API endpoints
@app.route('/')
def index():
    return "Welcome to JR Prayer Reminder API!"

@app.route('/add_reminder', methods=['POST'])
def add_reminder():
    data = request.get_json()
    if not data or 'user' not in data or 'time' not in data:
        abort(400, description="Missing required fields ('user' and 'time').")
    
    user = data['user']
    time_str = data['time']
    scripture = data.get('scripture', '')

    new_reminder = Reminder(user=user, time_str=time_str, scripture=scripture)
    db.session.add(new_reminder)
    db.session.commit()

    logger.info(f"Added reminder for {user} at {time_str}")
    return jsonify({"message": "Prayer reminder added!", "reminder": new_reminder.to_dict()}), 201

@app.route('/reminders', methods=['GET'])
def list_reminders():
    reminders = Reminder.query.all()
    return jsonify([reminder.to_dict() for reminder in reminders]), 200

@app.route('/reminder/<int:reminder_id>', methods=['PUT'])
def update_reminder(reminder_id):
    reminder = Reminder.query.get(reminder_id)
    if not reminder:
        abort(404, description="Reminder not found.")
    
    data = request.get_json()
    if 'user' in data:
        reminder.user = data['user']
    if 'time' in data:
        reminder.time_str = data['time']
    if 'scripture' in data:
        reminder.scripture = data['scripture']

    db.session.commit()
    logger.info(f"Updated reminder {reminder_id}")
    return jsonify({"message": "Reminder updated!", "reminder": reminder.to_dict()}), 200

@app.route('/reminder/<int:reminder_id>', methods=['DELETE'])
def delete_reminder(reminder_id):
    reminder = Reminder.query.get(reminder_id)
    if not reminder:
        abort(404, description="Reminder not found.")
    
    db.session.delete(reminder)
    db.session.commit()
    logger.info(f"Deleted reminder {reminder_id}")
    return jsonify({"message": "Reminder deleted!"}), 200

# Define the background notification worker
def notification_worker():
    # Wrap the entire loop in an application context
    with app.app_context():
        while True:
            now = datetime.now().strftime("%H:%M")
            today = date.today()
            reminders = Reminder.query.all()
            for reminder in reminders:
                if reminder.time_str == now and reminder.last_triggered_date != today:
                    message = f"🙏 Hey {reminder.user}, it's time to pray! Scripture: {reminder.scripture}"
                    logger.info(f"Triggering notification: {message}")
                    response = send_push_notification(message)
                    logger.info(f"Push notification response: {response}")
                    reminder.last_triggered_date = today
                    db.session.commit()
            time.sleep(60)  # Check every minute

# Start the notification thread AFTER the function is defined
notification_thread = threading.Thread(target=notification_worker, daemon=True)
notification_thread.start()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
