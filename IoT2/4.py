from flask import Flask, jsonify, request, send_from_directory
from flask_socketio import SocketIO
import random
import time
import threading
import csv
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app)

# Initialize the CSV file
csv_file = "abeta_data_log.csv"
with open(csv_file, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "Name", "Conductivity (µS/cm)", "Aβ1-42 Concentration (ng/mL)"])

# Function to simulate Aβ1-42 levels based on conductivity
def simulate_abeta_level(name="Unknown"):
    conductivity = random.uniform(100, 1000)  # Simulate conductivity values (in microSiemens/cm)
    abeta_concentration = (1000 - conductivity) / 15  # Adjust the formula as needed
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Log the data to CSV
    with open(csv_file, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, name, round(conductivity, 2), round(abeta_concentration, 2)])
    
    return {
        'timestamp': timestamp,
        'name': name,
        'conductivity': round(conductivity, 2),
        'abeta_concentration': round(abeta_concentration, 2)
    }


# Function to stream data to the frontend
def stream_data():
    while True:
        # Simulate data for demonstration purposes
        name = "John Doe"  # Example name (replace with data from ESP32-CAM)
        data = simulate_abeta_level(name)
        socketio.emit('new_data', data)
        time.sleep(random.randint(1, 5))

@app.route('/api/abeta', methods=['GET'])
def get_abeta_data():
    # Provide simulated data for testing
    data = simulate_abeta_level()
    return jsonify(data)

@app.route('/api/person', methods=['POST'])
def update_person():
    # Receive name and other details from the ESP32-CAM
    name = request.json.get('name', 'Unknown')
    simulate_abeta_level(name)  # Simulate and log with name
    return jsonify({"message": "Data received and logged"})

@app.route('/csv', methods=['GET'])
def download_csv():
    return send_from_directory('.', csv_file, as_attachment=True)

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/style.css')
def serve_css():
    return send_from_directory('static', 'style.css')

if __name__ == '__main__':
    threading.Thread(target=stream_data).start()
    socketio.run(app, debug=True)
