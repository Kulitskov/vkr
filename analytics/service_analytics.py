import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'db')))
from config import DATABASE_PATH

import sqlite3
from datetime import datetime, timedelta
from flask import Flask, jsonify

app = Flask(__name__)

def get_average_occupancy_time(camera_name):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT rectangle_index, status, timestamp
        FROM predictions
        WHERE camera_name = ? AND timestamp >= datetime('now', '-1 day')
        ORDER BY rectangle_index, timestamp
    ''', (camera_name,))
    results = cursor.fetchall()
    conn.close()
    
    occupancy_times = {}
    for rect_index, status, timestamp in results:
        if rect_index not in occupancy_times:
            occupancy_times[rect_index] = {'busy': 0, 'total': 0}
        if status == 'Busy':
            occupancy_times[rect_index]['busy'] += 1
        occupancy_times[rect_index]['total'] += 1
    
    average_occupancy = {}
    for rect_index, times in occupancy_times.items():
        total = times['total']
        busy = times['busy']
        average_occupancy[rect_index] = (busy / total) * 100 if total > 0 else 0
    
    return average_occupancy

def get_overall_average_occupancy_time(camera_name):
    average_times = get_average_occupancy_time(camera_name)
    total_time = sum(average_times.values())
    return total_time / len(average_times) if average_times else 0

def get_occupancy_percentage_by_hour(camera_name):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT rectangle_index, status, timestamp
        FROM predictions
        WHERE camera_name = ?
        ORDER BY timestamp
    ''', (camera_name,))
    results = cursor.fetchall()
    conn.close()
    
    hourly_data = {hour: {'busy': 0, 'free': 0} for hour in range(24)}
    for rect_index, status, timestamp in results:
        hour = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S').hour
        if status == 'Busy':
            hourly_data[hour]['busy'] += 1
        else:
            hourly_data[hour]['free'] += 1
    
    occupancy_percentage = {}
    for hour, data in hourly_data.items():
        total = data['busy'] + data['free']
        occupancy_percentage[hour] = (data['busy'] / total) * 100 if total > 0 else 0
    
    return occupancy_percentage

@app.route('/analytics/average_occupancy_time/<camera_name>', methods=['GET'])
def average_occupancy_time(camera_name):
    data = get_average_occupancy_time(camera_name)
    return jsonify(data)

@app.route('/analytics/overall_average_occupancy_time/<camera_name>', methods=['GET'])
def overall_average_occupancy_time(camera_name):
    data = get_overall_average_occupancy_time(camera_name)
    return jsonify(data)

@app.route('/analytics/occupancy_percentage_by_hour/<camera_name>', methods=['GET'])
def occupancy_percentage_by_hour(camera_name):
    data = get_occupancy_percentage_by_hour(camera_name)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, port=5002)
