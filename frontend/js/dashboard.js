// ===== Dashboard JavaScript =====
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
        duration_sec: parseInt(document.getElementById('duration-sec').value),
        interval_sec: parseInt(document.getElementById('interval-min').value) * 60
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
