# server.py
# No change from previous iteration - fully functioning as required.

import sqlite3
import os
import requests
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from threading import Thread

DB_NAME = 'availability.db'
app = Flask(__name__)

def get_utc_date():
    r = requests.head('https://www.google.com', timeout=5)
    date_str = r.headers.get('Date')
    utc_dt = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S GMT')
    return utc_dt

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS availability (
                 date TEXT PRIMARY KEY)''')
    conn.commit()
    conn.close()

def purge_old_data():
    utc_now = get_utc_date()
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM availability WHERE date < ?", (utc_now.strftime('%Y-%m-%d'),))
    conn.commit()
    conn.close()

def modify_availability(start_date, end_date):
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        print("Invalid date format.")
        return
    if end < start:
        print("End date cannot be before start date.")
        return
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    delta = (end - start).days
    for i in range(delta+1):
        day = start + timedelta(days=i)
        c.execute("REPLACE INTO availability (date) VALUES (?)", (day.strftime('%Y-%m-%d'),))
    conn.commit()
    conn.close()
    print("Availability updated.")

def data_dump():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT date FROM availability ORDER BY date ASC")
    rows = c.fetchall()
    conn.close()
    if not rows:
        print("No unavailable dates.")
    else:
        print("Unavailable dates:")
        for r in rows:
            print(r[0])

def get_availability_data():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT date FROM availability")
    rows = c.fetchall()
    conn.close()
    data = {}
    for r in rows:
        data[r[0]] = 'unavailable'
    return data

@app.route('/availability_data', methods=['GET'])
def availability_endpoint():
    data = get_availability_data()
    return jsonify(data)

@app.route('/add_unavailable', methods=['POST'])
def add_unavailable():
    content = request.json
    start_date = content.get('start')
    end_date = content.get('end')
    if not start_date or not end_date:
        return jsonify({"error": "Missing start or end date"}), 400
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400
    if end < start:
        return jsonify({"error": "End date cannot be before start date"}), 400

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    delta = (end - start).days
    for i in range(delta+1):
        day = start + timedelta(days=i)
        c.execute("REPLACE INTO availability (date) VALUES (?)", (day.strftime('%Y-%m-%d'),))
    conn.commit()
    conn.close()
    return jsonify({"message": "Availability updated"}), 200

@app.route('/purge_old', methods=['POST'])
def api_purge_old():
    utc_now = get_utc_date()
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM availability WHERE date < ?", (utc_now.strftime('%Y-%m-%d'),))
    deleted = c.rowcount
    conn.commit()
    conn.close()
    return jsonify({"message": f"Purged {deleted} old entries"}), 200

@app.route('/data_dump', methods=['GET'])
def api_data_dump():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT date FROM availability ORDER BY date ASC")
    rows = c.fetchall()
    conn.close()
    dates = [r[0] for r in rows]
    return jsonify({"unavailable_dates": dates})

def main_menu():
    while True:
        print("\nAvailability Management Menu")
        print("1. Modify availability for a date range")
        print("2. Purge outdated data")
        print("3. Data Dump (list all unavailable dates)")
        print("4. Exit")
        choice = input("Enter your choice: ").strip()

        if choice == '1':
            start = input("Enter start date (YYYY-MM-DD): ").strip()
            end = input("Enter end date (YYYY-MM-DD): ").strip()
            modify_availability(start, end)
        elif choice == '2':
            purge_old_data()
            print("Old data purged.")
        elif choice == '3':
            data_dump()
        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    if not os.path.exists(DB_NAME):
        init_db()
    purge_old_data()

    server_thread = Thread(target=app.run, kwargs={'host':'0.0.0.0','port':5000}, daemon=True)
    server_thread.start()

    main_menu()
