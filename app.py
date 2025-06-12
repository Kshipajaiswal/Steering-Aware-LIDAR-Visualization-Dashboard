from flask import Flask, render_template, jsonify
import threading
import time
from lidar_reader import get_latest_scan_data, get_car_steering_angle as calc_steering_angle, start_lidar_thread

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_scan_data')
def get_scan_data():
    data = get_latest_scan_data()
    return jsonify(data)

@app.route('/get_car_steering_angle')
def get_steering():
    data = get_latest_scan_data()
    angle = calc_steering_angle(data)
    return jsonify({'steering_angle': angle})

if __name__ == '__main__':
    start_lidar_thread()
    app.run(debug=True)
