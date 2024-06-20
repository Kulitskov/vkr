import sys
import os

from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
import json
import re
import requests
import cv2
from io import BytesIO
from PIL import Image

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'db')))

app = Flask(__name__)

DATA_DIR = 'data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

with open('main/static/cams.json') as f:
    cameras = json.load(f)

def sanitize_filename(filename):
    return re.sub(r'[^a-zA-Z0-9_-]', '_', filename)

rectangles = {}

@app.route('/')
def index():
    return redirect(url_for('markup'))

@app.route('/markup')
def markup():
    return render_template('markup.html', cameras=cameras)

@app.route('/display')
def display():
    return render_template('display.html', cameras=cameras)

@app.route('/analytics')
def analytics():
    return render_template('analytics.html', cameras=cameras)

@app.route('/save_rectangles', methods=['POST'])
def save_rectangles():
    data = request.json
    camera_name = data['camera']
    rectangles[camera_name] = data['rectangles']
    sanitized_name = sanitize_filename(camera_name)
    with open(os.path.join(DATA_DIR, f'{sanitized_name}.json'), 'w') as f:
        json.dump(data['rectangles'], f)
    return jsonify({'status': 'success'})

@app.route('/get_rectangles/<camera_name>', methods=['GET'])
def get_rectangles(camera_name):
    sanitized_name = sanitize_filename(camera_name)
    if camera_name in rectangles:
        return jsonify(rectangles[camera_name])
    elif os.path.exists(os.path.join(DATA_DIR, f'{sanitized_name}.json')):
        with open(os.path.join(DATA_DIR, f'{sanitized_name}.json'), 'r') as f:
            rectangles[camera_name] = json.load(f)
            return jsonify(rectangles[camera_name])
    else:
        return jsonify([])

@app.route('/frame/<camera_name>')
def get_frame(camera_name):
    if camera_name not in cameras:
        return "Camera not found", 404

    rtsp_url = cameras[camera_name]
    frame_bytes = get_frame_from_rtsp(rtsp_url)
    if frame_bytes is None:
        return "Failed to capture frame", 500
    
    return send_file(BytesIO(frame_bytes), mimetype='image/jpeg')

def get_frame_from_rtsp(rtsp_url):
    cap = cv2.VideoCapture(rtsp_url)
    ret, frame = cap.read()
    cap.release()
    if ret:
        _, img_encoded = cv2.imencode('.jpg', frame)
        return img_encoded.tobytes()
    else:
        return None

@app.route('/analytics/average_occupancy_time/<camera_name>', methods=['GET'])
def average_occupancy_time(camera_name):
    response = requests.get(f'http://127.0.0.1:5002/analytics/average_occupancy_time/{camera_name}')
    return jsonify(response.json())

@app.route('/analytics/overall_average_occupancy_time/<camera_name>', methods=['GET'])
def overall_average_occupancy_time(camera_name):
    response = requests.get(f'http://127.0.0.1:5002/analytics/overall_average_occupancy_time/{camera_name}')
    return jsonify(response.json())

@app.route('/analytics/occupancy_percentage_by_hour/<camera_name>', methods=['GET'])
def occupancy_percentage_by_hour(camera_name):
    response = requests.get(f'http://127.0.0.1:5002/analytics/occupancy_percentage_by_hour/{camera_name}')
    return jsonify(response.json())

@app.route('/save_cameras', methods=['POST'])
def save_cameras():
    global cameras
    
    new_cameras = request.json
    with open('main/static/cams.json', 'w') as f:
        json.dump(new_cameras, f)
    
    with open('main/static/cams.json') as f:
        cameras = json.load(f)
    return jsonify({'status': 'success'})


if __name__ == '__main__':
    app.run(debug=True)
