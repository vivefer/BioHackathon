from flask import Flask, jsonify, request, send_from_directory
from flask_socketio import SocketIO
import csv
import random
from datetime import datetime
import time
from threading import Thread

app = Flask(__name__)
socketio = SocketIO(app)

# CSV File Initialization
csv_file = "abeta_data_log.csv"
with open(csv_file, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "Name", "Conductivity (µS/cm)", "Aβ1-42 Concentration (ng/mL)"])

# State to switch between simulated and real data
real_data_active = False

# Function to log data into CSV
def log_abeta_data(name, conductivity, abeta_concentration):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(csv_file, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, name, round(conductivity, 2), round(abeta_concentration, 2)])
    return {
        'timestamp': timestamp,
        'name': name,
        'conductivity': round(conductivity, 2),
        'abeta_concentration': round(abeta_concentration, 2)
    }

# Simulated data generator
def simulate_data():
    global real_data_active
    while True:
        if not real_data_active:  # Only simulate if no real data is active
            name = "Simulated Person"
            conductivity = random.uniform(0.5, 2.0)
            abeta_concentration = random.uniform(10, 40)
            simulated_data = log_abeta_data(name, conductivity, abeta_concentration)
            socketio.emit('new_data', simulated_data)
        time.sleep(2)  # Adjust frequency as needed

# Route to receive data from ESP32-CAM
@app.route('/api/person', methods=['POST'])
def receive_data_from_esp32():
    global real_data_active
    real_data_active = True  # Switch to real data
    data = request.json
    name = data.get('name', 'Unknown')
    conductivity = data.get('conductivity', 10.0)
    abeta_concentration = data.get('abeta_concentration', 0.0)

    # Log and emit data
    logged_data = log_abeta_data(name, conductivity, abeta_concentration)
    socketio.emit('new_data', logged_data)
    return jsonify({"message": "Real data received and logged"})

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
    # Start the simulated data thread
    simulated_thread = Thread(target=simulate_data)
    simulated_thread.daemon = True
    simulated_thread.start()

    # Run the Flask server on all available IPs
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
