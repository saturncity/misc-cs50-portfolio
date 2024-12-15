from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///availability.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Availability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), unique=True, nullable=False)  # Format: YYYY-MM-DD
    status = db.Column(db.String(20), nullable=False)  # "available" or "unavailable"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/availability_data')
def get_availability():
    today = datetime.utcnow().date()
    end_date = today + timedelta(days=90)
    records = Availability.query.filter(
        db.func.date(Availability.date) >= today,
        db.func.date(Availability.date) <= end_date
    ).all()
    availability = {record.date: record.status for record in records}
    return jsonify(availability)

@app.route('/update_availability', methods=['POST'])
def update_availability():
    data = request.json
    date = data.get('date')
    status = data.get('status')

    if not date:
        return jsonify({'error': 'Invalid input'}), 400

    if not status:  # If status is empty, delete the record
        record = Availability.query.filter_by(date=date).first()
        if record:
            db.session.delete(record)
            db.session.commit()
        return jsonify({'success': True})

    # Add or update the record
    record = Availability.query.filter_by(date=date).first()
    if record:
        record.status = status
    else:
        record = Availability(date=date, status=status)
        db.session.add(record)
    db.session.commit()
    return jsonify({'success': True})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
