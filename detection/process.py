import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'db')))

from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
from PIL import Image
from io import BytesIO
import requests
import torch
import torchvision.transforms as transforms
from database import insert_prediction

app = Flask(__name__)
CORS(app)

model_path = 'detection/model.pth'
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = torch.load(model_path, map_location=device)
model.eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def get_frame_from_rtsp(rtsp_url):
    cap = cv2.VideoCapture(rtsp_url)
    ret, frame = cap.read()
    cap.release()
    if ret:
        _, img_encoded = cv2.imencode('.jpg', frame)
        return img_encoded.tobytes()
    else:
        return None

@app.route('/process_image', methods=['POST'])
def process_image():
    data = request.json
    camera = data['camera']
    rectangles = data['rectangles']
    rtsp_url = data['rtsp_url']
    
    frame_bytes = get_frame_from_rtsp(rtsp_url)
    if frame_bytes is None:
        return jsonify({'error': 'Failed to capture frame'}), 500
    
    img = Image.open(BytesIO(frame_bytes))
    
    colors = []
    for i, rect in enumerate(rectangles):
        x_coords = [point['x'] for point in rect]
        y_coords = [point['y'] for point in rect]
        left = max(0, min(x_coords) - 10)
        upper = max(0, min(y_coords) - 10)
        right = min(img.width, max(x_coords) + 10)
        lower = min(img.height, max(y_coords) + 10)
        
        cropped_img = img.crop((left, upper, right, lower))
        
        input_tensor = transform(cropped_img).unsqueeze(0).to(device)
        
        with torch.no_grad():
            output = model(input_tensor)
            _, predicted = torch.max(output, 1)
        
        if predicted.item() == 1:
            status = 'Free'
            color = '#00FF00'
        else:
            status = 'Busy'
            color = '#FF0000'
        
        insert_prediction(camera, i, status)
        
        colors.append(color)
    
    return jsonify({'colors': colors})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
