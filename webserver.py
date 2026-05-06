# -*- coding: utf-8 -*-
"""
Webserver Dashboard - Flask

Chạy trên laptop để điều khiển mạch Yolobit từ xa.

Cách chạy:
  1. Cài Flask: pip install flask
  2. Chạy: python webserver.py
  3. Mở browser: http://localhost:5000

API Endpoints:
  - GET  /              : Hiển thị dashboard HTML
  - POST /api/data      : Nhận dữ liệu từ Yolobit
  - GET  /api/command   : Trả về lệnh cho Yolobit (hoặc empty)
  - POST /api/command   : Gửi lệnh (từ web frontend)
"""

from flask import Flask, render_template_string, request, jsonify
import json
import os
from datetime import datetime
from threading import Lock

app = Flask(__name__)

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
        
        print(f"[WEBSERVER] Data received: T={data.get('temperature')}°C, H={data.get('humidity')}%")
        return jsonify({"status": "ok"}), 200
    
    except Exception as e:
        print(f"[WEBSERVER] Error receiving data: {e}")
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
        print(f"[WEBSERVER] Command sent to device: {cmd.get('command')}")
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
        
        print(f"[WEBSERVER] Command queued: {cmd.get('command')}")
        return jsonify({"status": "queued"}), 200
    
    except Exception as e:
        print(f"[WEBSERVER] Error queuing command: {e}")
        return jsonify({"error": str(e)}), 400


@app.route('/api/status', methods=['GET'])
def api_get_status():
    """Lấy trạng thái hiện tại của thiết bị."""
    with data_lock:
        return jsonify(device_data), 200


# ===== Web Frontend =====

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Yolobit Dashboard - Điều khiển Máy Bơm</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .status-bar {
            background: rgba(255, 255, 255, 0.1);
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .status-bar span {
            font-size: 0.9em;
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            transition: transform 0.3s;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        .card h2 {
            color: #333;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        
        .sensor-data {
            display: flex;
            justify-content: space-around;
            margin-bottom: 20px;
        }
        
        .sensor-item {
            text-align: center;
        }
        
        .sensor-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }
        
        .sensor-label {
            color: #666;
            font-size: 0.9em;
        }
        
        .controls {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        .control-group {
            margin-bottom: 15px;
        }
        
        .control-group label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
        }
        
        select, input, button {
            width: 100%;
            padding: 10px;
            border: 2px solid #e0e0e0;
            border-radius: 5px;
            font-size: 1em;
            transition: border-color 0.3s;
        }
        
        select:focus, input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        button {
            background: #667eea;
            color: white;
            border: none;
            cursor: pointer;
            font-weight: 600;
            transition: background 0.3s;
        }
        
        button:hover {
            background: #5568d3;
        }
        
        button:active {
            transform: scale(0.98);
        }
        
        .button-group {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }
        
        .btn-on {
            background: #4caf50;
        }
        
        .btn-on:hover {
            background: #45a049;
        }
        
        .btn-off {
            background: #f44336;
        }
        
        .btn-off:hover {
            background: #da190b;
        }
        
        .status-indicator {
            display: inline-block;
            width: 15px;
            height: 15px;
            border-radius: 50%;
            margin-right: 8px;
            vertical-align: middle;
        }
        
        .status-on {
            background: #4caf50;
        }
        
        .status-off {
            background: #f44336;
        }
        
        .mode-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            margin-top: 10px;
        }
        
        .mode-manual {
            background: #ff9800;
            color: white;
        }
        
        .mode-auto {
            background: #2196f3;
            color: white;
        }
        
        .mode-scheduled {
            background: #9c27b0;
            color: white;
        }
        
        .info-text {
            color: #666;
            font-size: 0.9em;
            margin-top: 10px;
            padding: 10px;
            background: #f5f5f5;
            border-radius: 5px;
        }
        
        .last-update {
            color: #999;
            font-size: 0.8em;
            margin-top: 10px;
        }
        
        footer {
            text-align: center;
            color: white;
            margin-top: 30px;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚰 Yolobit Dashboard</h1>
            <p>Điều khiển thiết bị từ xa</p>
        </header>
        
        <div class="status-bar">
            <span>
                <span class="status-indicator" id="wifi-status" style="background: #999;"></span>
                WiFi: <span id="wifi-text">Đang kiểm tra...</span>
            </span>
            <span id="last-update">Cập nhật lần cuối: ---</span>
        </div>
        
        <div class="dashboard">
            <!-- Cảm biến Nhiệt độ & Độ ẩm -->
            <div class="card">
                <h2>📊 Cảm Biến (DHT20)</h2>
                <div class="sensor-data">
                    <div class="sensor-item">
                        <div class="sensor-label">Nhiệt độ</div>
                        <div class="sensor-value" id="temp-value">--°C</div>
                    </div>
                    <div class="sensor-item">
                        <div class="sensor-label">Độ ẩm</div>
                        <div class="sensor-value" id="humidity-value">--%</div>
                    </div>
                </div>
                <div class="info-text">
                    📍 Đọc từ DHT20 qua I2C
                </div>
                <div class="last-update" id="sensor-update"></div>
            </div>
            
            <!-- Cảm biến Đất & Ánh sáng -->
            <div class="card">
                <h2>🌱 Cảm Biến Đất & Ánh Sáng</h2>
                <div class="sensor-data">
                    <div class="sensor-item">
                        <div class="sensor-label">Độ ẩm đất</div>
                        <div class="sensor-value" id="sm-value">--%</div>
                    </div>
                    <div class="sensor-item">
                        <div class="sensor-label">Ánh sáng</div>
                        <div class="sensor-value" id="lux-value">--</div>
                    </div>
                </div>
                <div class="info-text">
                    📍 Pin1: Cảm biến độ ẩm | Pin2: Cảm biến ánh sáng
                </div>
                <div class="last-update" id="soil-light-update"></div>
            </div>
            
            <!-- Điều khiển Máy bơm -->
            <div class="card">
                <h2>💧 Máy Bơm</h2>
                
                <div class="control-group">
                    <label>Trạng thái:</label>
                    <div style="padding: 10px; background: #f5f5f5; border-radius: 5px;">
                        <span class="status-indicator" id="pump-status-indicator" style="background: #f44336;"></span>
                        <span id="pump-status-text">TẮT</span>
                    </div>
                </div>
                
                <div class="button-group">
                    <button class="btn-on" onclick="sendCommand('set_pump_state', {state: 1})">
                        Bật ✓
                    </button>
                    <button class="btn-off" onclick="sendCommand('set_pump_state', {state: 0})">
                        Tắt ✗
                    </button>
                </div>
                
                <div class="info-text" id="pump-info" style="margin-top: 10px;">
                    Mode: <span id="pump-mode">manual</span>
                </div>
            </div>
            
            <!-- Chế độ hoạt động -->
            <div class="card">
                <h2>⚙️ Chế độ</h2>
                
                <div class="control-group">
                    <label>Chọn chế độ:</label>
                    <select id="mode-select" onchange="changePumpMode()">
                        <option value="manual">Manual (Thủ công)</option>
                        <option value="auto">Auto (Theo độ ẩm)</option>
                        <option value="scheduled">Scheduled (Hẹn giờ)</option>
                    </select>
                </div>
                
                <!-- Auto mode -->
                <div id="auto-mode" style="display: none;">
                    <div class="control-group">
                        <label>Ngưỡng độ ẩm (%):</label>
                        <div style="display: flex; gap: 10px;">
                            <input type="range" id="threshold-slider" min="0" max="100" value="50" 
                                   onchange="updateThresholdDisplay()">
                            <input type="number" id="threshold-input" min="0" max="100" value="50" 
                                   style="width: 60px;" onchange="syncThreshold()">
                        </div>
                        <button onclick="sendCommand('set_humidity_threshold', 
                                {threshold: parseFloat(document.getElementById('threshold-input').value)})">
                            Áp dụng
                        </button>
                    </div>
                </div>
                
                <!-- Scheduled mode -->
                <div id="scheduled-mode" style="display: none;">
                    <div class="control-group">
                        <label>Giờ bắt đầu:</label>
                        <input type="number" id="start-hour" min="0" max="23" value="6" placeholder="Giờ">
                        <input type="number" id="start-min" min="0" max="59" value="0" placeholder="Phút" style="margin-top: 5px;">
                    </div>
                    
                    <div class="control-group">
                        <label>Giờ kết thúc:</label>
                        <input type="number" id="end-hour" min="0" max="23" value="22" placeholder="Giờ">
                        <input type="number" id="end-min" min="0" max="59" value="0" placeholder="Phút" style="margin-top: 5px;">
                    </div>
                    
                    <div class="control-group">
                        <label>Thời gian chạy (giây):</label>
                        <input type="number" id="duration-sec" min="1" max="3600" value="15" placeholder="Giây">
                    </div>
                    
                    <button onclick="sendSchedule()">Áp dụng Lịch</button>
                </div>
            </div>
        </div>
        
        <footer>
            <p>✨ Yolobit + Webserver Dashboard | Flask + HTML5</p>
        </footer>
    </div>
    
    <script>
        // Cập nhật dữ liệu từ server mỗi 1 giây
        setInterval(updateDashboard, 1000);
        
        async function updateDashboard() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                // Cập nhật cảm biến
                const temp = data.temperature !== null ? data.temperature.toFixed(1) : '--';
                const humidity = data.humidity !== null ? data.humidity.toFixed(1) : '--';
                
                document.getElementById('temp-value').textContent = temp + '°C';
                document.getElementById('humidity-value').textContent = humidity + '%';
                
                // Cập nhật cảm biến đất & ánh sáng
                const sm = data.soil_moisture !== null ? data.soil_moisture.toFixed(0) : '--';
                const lux = data.light_level !== null ? data.light_level.toFixed(0) : '--';
                
                document.getElementById('sm-value').textContent = sm + '%';
                document.getElementById('lux-value').textContent = lux;
                
                // Cập nhật máy bơm
                const pumpStatus = data.pump_state ? 'BẬT' : 'TẮT';
                const pumpColor = data.pump_state ? '#4caf50' : '#f44336';
                document.getElementById('pump-status-text').textContent = pumpStatus;
                document.getElementById('pump-status-indicator').style.background = pumpColor;
                
                // Cập nhật mode badge
                const modeBadge = 'mode-' + data.pump_mode.toLowerCase();
                document.getElementById('pump-mode').textContent = data.pump_mode.toUpperCase();
                
                // Cập nhật thời gian
                const now = new Date().toLocaleTimeString('vi-VN');
                document.getElementById('last-update').textContent = 'Cập nhật lần cuối: ' + now;
                
                // Giả lập WiFi connected (luôn true)
                document.getElementById('wifi-status').style.background = '#4caf50';
                document.getElementById('wifi-text').textContent = 'Kết nối';
                
            } catch (error) {
                console.error('Error updating dashboard:', error);
                document.getElementById('wifi-status').style.background = '#f44336';
                document.getElementById('wifi-text').textContent = 'Mất kết nối';
            }
        }
        
        function changePumpMode() {
            const mode = document.getElementById('mode-select').value;
            
            // Ẩn/hiện các control dựa vào mode
            document.getElementById('auto-mode').style.display = mode === 'auto' ? 'block' : 'none';
            document.getElementById('scheduled-mode').style.display = mode === 'scheduled' ? 'block' : 'none';
            
            // Gửi lệnh đổi mode
            sendCommand('set_pump_mode', { mode: mode });
        }
        
        function updateThresholdDisplay() {
            const slider = document.getElementById('threshold-slider');
            const input = document.getElementById('threshold-input');
            input.value = slider.value;
        }
        
        function syncThreshold() {
            const input = document.getElementById('threshold-input');
            const slider = document.getElementById('threshold-slider');
            slider.value = input.value;
        }
        
        function sendSchedule() {
            const params = {
                start_hour: parseInt(document.getElementById('start-hour').value),
                start_min: parseInt(document.getElementById('start-min').value),
                end_hour: parseInt(document.getElementById('end-hour').value),
                end_min: parseInt(document.getElementById('end-min').value),
                duration_sec: parseInt(document.getElementById('duration-sec').value)
            };
            
            sendCommand('set_schedule', params);
        }
        
        async function sendCommand(command, params) {
            try {
                const payload = { command, params };
                
                const response = await fetch('/api/command', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });
                
                if (response.ok) {
                    console.log(`✓ Lệnh gửi: ${command}`);
                } else {
                    console.error('Error sending command');
                }
            } catch (error) {
                console.error('Error:', error);
            }
        }
        
        // Cập nhật ngay khi load trang
        updateDashboard();
    </script>
</body>
</html>
"""


@app.route('/', methods=['GET'])
def index():
    """Hiển thị dashboard HTML."""
    return render_template_string(HTML_TEMPLATE)


# ===== Main =====

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Yolobit Webserver Dashboard")
    print("=" * 60)
    print(f"📱 Mở browser: http://localhost:5000")
    print(f"📊 API endpoints:")
    print(f"   - POST /api/data      : Nhận dữ liệu từ Yolobit")
    print(f"   - GET  /api/command   : Trả lệnh cho Yolobit")
    print(f"   - POST /api/command   : Gửi lệnh (từ web)")
    print(f"   - GET  /api/status    : Lấy trạng thái hiện tại")
    print("=" * 60)
    print()
    
    # Chạy Flask server
    app.run(host='0.0.0.0', port=5000, debug=True)
