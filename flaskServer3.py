# File: server.py

from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from geopy.distance import geodesic

app = Flask(__name__)

# PostgreSQL database configuration
DB_NAME = "phone_numbers_db"
DB_USER = "your_username"
DB_PASS = "your_password"
DB_HOST = "localhost"
DB_PORT = "5432"

def get_db_connection():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )
    return conn

@app.route('/api/register_phone_number', methods=['POST'])
def register_phone_number():
    data = request.get_json()
    number = data['number']
    name = data['name']
    latitude = data['latitude']
    longitude = data['longitude']

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO phone_numbers (number, name, latitude, longitude) VALUES (%s, %s, %s, %s)",
        (number, name, latitude, longitude)
    )
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Phone number registered successfully."}), 201

@app.route('/api/find_nearest', methods=['GET'])
def find_nearest():
    user_lat = float(request.args.get('latitude'))
    user_lon = float(request.args.get('longitude'))

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM phone_numbers")
    phone_numbers = cur.fetchall()
    cur.close()
    conn.close()

    nearest_phone = None
    min_distance = float('inf')

    for phone in phone_numbers:
        phone_location = (phone['latitude'], phone['longitude'])
        user_location = (user_lat, user_lon)
        distance = geodesic(user_location, phone_location).km

        if distance < min_distance:
            min_distance = distance
            nearest_phone = phone

    if nearest_phone:
        return jsonify({
            "number": nearest_phone['number'],
            "name": nearest_phone['name'],
            "latitude": nearest_phone['latitude'],
            "longitude": nearest_phone['longitude'],
            "distance": min_distance
        })
    else:
        return jsonify({"message": "No phone numbers found."}), 404

if __name__ == '__main__':
    app.run(debug=True)