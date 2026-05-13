# -*- coding: utf-8 -*-
"""
Backend API Server - Flask

Chạy trên laptop để điều khiển mạch Yolobit từ xa.

Cách chạy:
  1. Cài Flask: pip install flask
  2. Chạy: python backend/app.py
  3. Mở browser: http://localhost:5000

API Endpoints:
  - GET  /              : Hiển thị dashboard HTML (serve từ frontend/)
  - POST /api/data      : Nhận dữ liệu từ Yolobit
  - GET  /api/command   : Trả về lệnh cho Yolobit (hoặc empty)
  - POST /api/command   : Gửi lệnh (từ web frontend)
  - GET  /api/status    : Lấy trạng thái hiện tại
"""

import os
import sys
import io
from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime
from threading import Lock

# Fix encoding cho Windows console (hỗ trợ emoji)
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Đường dẫn tới thư mục frontend (ngang hàng với backend/)
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend')

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')

# Khóa để tránh race condition
data_lock = Lock()

# Lưu dữ liệu mới nhất từ Yolobit
device_data = {
    "timestamp": 0,
    "temperature": None,
    "humidity": None,
    "soil_moisture": None,
    "light_level": None,
    "pump_state": 0,
    "pump_mode": "manual",
    "humidity_threshold": 50.0,
}

# Lệnh chờ xử lý (Yolobit sẽ lấy)
pending_command = None


# ===== API Endpoints =====

@app.route('/api/data', methods=['POST'])
def api_receive_data():
    """
    Nhận dữ liệu từ Yolobit.
    Body: {temperature, humidity, pump_state, pump_mode, ...}
    """
    global device_data
    
    try:
        data = request.get_json()
        
        with data_lock:
            device_data.update(data)
            device_data["timestamp"] = datetime.now().isoformat()
        
        print(f"[BACKEND] Data received: T={data.get('temperature')}°C, H={data.get('humidity')}%")
        return jsonify({"status": "ok"}), 200
    
    except Exception as e:
        print(f"[BACKEND] Error receiving data: {e}")
        return jsonify({"error": str(e)}), 400


@app.route('/api/command', methods=['GET'])
def api_get_command():
    """
    Trả về lệnh cho Yolobit.
    Response: {command: "set_mode", params: {mode: "auto"}}
    """
    global pending_command
    
    with data_lock:
        cmd = pending_command
        pending_command = None  # Xóa lệnh sau khi gửi
    
    if cmd:
        print(f"[BACKEND] Command sent to device: {cmd.get('command')}")
        return jsonify(cmd), 200
    else:
        return jsonify({}), 200  # Empty response


@app.route('/api/command', methods=['POST'])
def api_send_command():
    """
    Gửi lệnh từ web frontend đến Yolobit.
    Body: {command: "set_pump_mode", params: {mode: "auto"}}
    """
    global pending_command
    
    try:
        cmd = request.get_json()
        
        with data_lock:
            pending_command = cmd
        
        print(f"[BACKEND] Command queued: {cmd.get('command')}")
        return jsonify({"status": "queued"}), 200
    
    except Exception as e:
        print(f"[BACKEND] Error queuing command: {e}")
        return jsonify({"error": str(e)}), 400


@app.route('/api/status', methods=['GET'])
def api_get_status():
    """Lấy trạng thái hiện tại của thiết bị."""
    with data_lock:
        return jsonify(device_data), 200


# ===== Serve Frontend =====

@app.route('/', methods=['GET'])
def index():
    """Serve trang dashboard HTML từ thư mục frontend/."""
    return send_from_directory(FRONTEND_DIR, 'index.html')


# ===== Main =====

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Yolobit Backend API Server")
    print("=" * 60)
    print(f"📱 Mở browser: http://localhost:5000")
    print(f"📂 Frontend:   {FRONTEND_DIR}")
    print(f"📊 API endpoints:")
    print(f"   - POST /api/data      : Nhận dữ liệu từ Yolobit")
    print(f"   - GET  /api/command   : Trả lệnh cho Yolobit")
    print(f"   - POST /api/command   : Gửi lệnh (từ web)")
    print(f"   - GET  /api/status    : Lấy trạng thái hiện tại")
    print("=" * 60)
    print()
    
    # Chạy Flask server
    app.run(host='0.0.0.0', port=5000, debug=True)
