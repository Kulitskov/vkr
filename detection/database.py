import os
import sys

# Добавление пути к файлу config.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'db')))
from config import DATABASE_PATH

import sqlite3

def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            camera_name TEXT,
            rectangle_index INTEGER,
            status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def insert_prediction(camera_name, rectangle_index, status):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO predictions (camera_name, rectangle_index, status)
        VALUES (?, ?, ?)
    ''', (camera_name, rectangle_index, status))
    conn.commit()
    conn.close()

def get_predictions(camera_name):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT rectangle_index, status, timestamp
        FROM predictions
        WHERE camera_name = ?
    ''', (camera_name,))
    results = cursor.fetchall()
    conn.close()
    return results

init_db()
 