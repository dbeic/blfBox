from flask import Flask, request, jsonify
from geopy.distance import geodesic
import psycopg2
import psycopg2.extras

app = Flask(__name__)

# PostgreSQL database configuration
DB_HOST = 'localhost'
DB_NAME = 'phone_numbers_db'
DB_USER = 'username'
DB_PASS = 'password'

def get_db_connection():
    conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
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
        'INSERT INTO phone_numbers (number, name, latitude, longitude) VALUES (%s, %s, %s, %s)',
        (number, name, latitude, longitude)
    )
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': 'Phone number registered successfully'}), 201

@app.route('/api/find_nearest', methods=['GET'])
def find_nearest():
    user_lat = float(request.args.get('latitude'))
    user_lon = float(request.args.get('longitude'))

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM phone_numbers')
    phone_numbers = cur.fetchall()
    cur.close()
    conn.close()

    if not phone_numbers:
        return jsonify({'message': 'No phone numbers found'}), 404

    nearest_phone = None
    min_distance = float('inf')

    for phone_number in phone_numbers:
        lat = phone_number['latitude']
        lon = phone_number['longitude']
        distance = geodesic((user_lat, user_lon), (lat, lon)).meters
        if distance < min_distance:
            min_distance = distance
            nearest_phone = {
                'number': phone_number['number'],
                'name': phone_number['name'],
                'distance': min_distance
            }

    if nearest_phone:
        return jsonify(nearest_phone), 200
    else:
        return jsonify({'message': 'No phone numbers found'}), 404

if __name__ == '__main__':
    app.run(debug=True)