# Yolobit IoT Backend - FastAPI

Backend FastAPI cho hệ thống IoT Yolobit, cung cấp API REST và dashboard để điều khiển máy bơm, cảm biến, và lưu trữ dữ liệu.

## 🎯 Tổng Quan

- **Framework**: FastAPI
- **Database**: SQLite 3 với WAL mode
- **Architecture**: Clean Architecture (Router → Service → Repository → DB)
- **Storage**: `iot_data.db` lưu toàn bộ lịch sử sensor
- **Dashboard**: HTML5 được trả từ route `/` (lấy từ `frontend/index.html`)

## 📁 Cấu Trúc Thư Mục

```
backend/
├── __init__.py
├── app.py                          # FastAPI app entrypoint, route "/", CORS
├── api/
│   ├── __init__.py
│   ├── routers/
│   │   ├── __init__.py
│   │   └── device.py               # Router: POST /api/data, GET /api/command, etc.
│   ├── services/
│   │   ├── __init__.py
│   │   └── device_service.py       # Business logic: save_device_data, queue_command, get_history
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── memory_repository.py    # Repository: cache + DB access, gọi DBManager
│   └── schemas/
│       ├── __init__.py
│       ├── device.py               # Pydantic: DeviceData, DeviceStatus
│       ├── command.py              # Pydantic: Command
│       └── history.py              # Pydantic: SensorHistoryRecord, SensorHistoryResponse
├── db/
│   ├── __init__.py
│   └── db_manager.py               # SQLite manager: create table, insert, query
├── core/
│   ├── __init__.py
│   └── dependencies.py             # DI: DBManager, Repository, Service
└── tests/
    ├── __init__.py
    └── test_device_service.py      # Unit tests với pytest
```

## 🚀 Cách Chạy

### 1. Cài Dependencies

```bash
pip install -r requirements.txt
```

### 2. Chạy Backend

```bash
# Chạy ở port 5000 (mặc định Flask cũ)
uvicorn backend.app:app --reload --host 0.0.0.0 --port 5000

# Hoặc mặc định port 8000
uvicorn backend.app:app --reload
```

### 3. Mở Dashboard

- **Từ cùng máy**: `http://localhost:5000` hoặc `http://localhost:8000`
- **Từ máy khác**: `http://<IP_LAPTOP>:5000`

## 📡 API Endpoints

### Core Endpoints

| Method | Endpoint | Mô Tả | Request Body | Response |
|--------|----------|--------|--------------|----------|
| GET | `/` | Trả HTML dashboard | N/A | HTML page |
| POST | `/api/data` | Nhận dữ liệu từ Yolobit | `DeviceData` | `{"status": "ok"}` |
| GET | `/api/status` | Lấy trạng thái hiện tại | N/A | `DeviceStatus` |
| GET | `/api/command` | Lấy lệnh chờ xử lý | N/A | `Command` hoặc `{}` |
| POST | `/api/command` | Gửi lệnh cho Yolobit | `Command` | `{"status": "queued"}` |
| GET | `/api/history` | Lấy lịch sử sensor (phân trang) | `limit`, `offset` (query) | `SensorHistoryResponse` |

### Schema Request/Response

#### `POST /api/data` - DeviceData
```json
{
  "timestamp": 1700000000.0,
  "temperature": 25.5,
  "humidity": 60.0,
  "soil_moisture": 42,
  "light_level": 2100,
  "pump_state": 1,
  "pump_mode": "auto",
  "humidity_threshold": 55.0
}
```

#### `GET /api/status` - DeviceStatus
```json
{
  "timestamp": 1700000000.0,
  "temperature": 25.5,
  "humidity": 60.0,
  "soil_moisture": 42,
  "light_level": 2100,
  "pump_state": 1,
  "pump_mode": "auto",
  "humidity_threshold": 55.0
}
```

#### `POST /api/command` & `GET /api/command` - Command
```json
{
  "command": "set_pump_mode",
  "params": {"mode": "auto"}
}
```

Các lệnh hỗ trợ:
- `set_pump_state`: `{"state": 0|1}`
- `set_pump_mode`: `{"mode": "manual|auto|scheduled"}`
- `set_humidity_threshold`: `{"threshold": 50.0}`
- `set_schedule`: `{"start_hour": 6, "start_min": 0, "end_hour": 22, "end_min": 0, "duration_sec": 15}`

#### `GET /api/history?limit=100&offset=0` - SensorHistoryResponse
```json
{
  "total": 1250,
  "count": 100,
  "offset": 0,
  "records": [
    {
      "id": 1250,
      "timestamp": 1700000100.0,
      "temperature": 25.6,
      "humidity": 59.8,
      "soil_moisture": 41,
      "light_level": 2110,
      "pump_state": 1,
      "pump_mode": "auto",
      "humidity_threshold": 55.0
    },
    ...
  ]
}
```

## 🗄️ Database Schema

### Table: `SensorHistory`

```sql
CREATE TABLE SensorHistory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL NOT NULL,
    temperature REAL,
    humidity REAL,
    soil_moisture INTEGER,
    light_level INTEGER,
    pump_state INTEGER NOT NULL,
    pump_mode TEXT NOT NULL,
    humidity_threshold REAL NOT NULL
);

-- Index để query nhanh theo thời gian
CREATE INDEX idx_timestamp ON SensorHistory(timestamp);
```

### Tính Năng SQLite

- **WAL Mode**: `PRAGMA journal_mode=WAL;` - tối ưu cho many-reads
- **Synchronous**: `PRAGMA synchronous = NORMAL;` - tốc độ vs độ an toàn cân bằng
- **Timeout**: 30 giây khi có nhiều connection

## 🏗️ Kiến Trúc Clean Architecture

### 1. **Router** (`backend/api/routers/device.py`)
- Tiếp nhận request HTTP
- Validate request body bằng Pydantic schema
- Gọi service methods
- Trả response

### 2. **Service** (`backend/api/services/device_service.py`)
- Business logic
- Xử lý dữ liệu trước khi lưu
- Orchestrate repository calls
- Không biết về HTTP details

### 3. **Repository** (`backend/api/repositories/memory_repository.py`)
- Cache dữ liệu hiện tại trong bộ nhớ
- Gọi DBManager để lưu vào DB
- Quản lý lệnh chờ xử lý
- Interface giữa service và database

### 4. **Database** (`backend/db/db_manager.py`)
- Tạo/khởi tạo SQLite database
- `INSERT` record vào `SensorHistory`
- `SELECT` lịch sử với phân trang
- Quản lý connection pool

### 5. **Dependency Injection** (`backend/core/dependencies.py`)
- Khởi tạo `DBManager` (tạo `iot_data.db`)
- Khởi tạo `Repository` (gắn DBManager)
- Khởi tạo `Service` (gắn Repository)
- FastAPI dependency injection: `get_device_service()`

## 📝 Ví Dụ Sử Dụng

### Client gửi dữ liệu cảm biến

```bash
curl -X POST http://localhost:5000/api/data \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": 1700000000.0,
    "temperature": 25.5,
    "humidity": 60.0,
    "soil_moisture": 42,
    "light_level": 2100,
    "pump_state": 1,
    "pump_mode": "auto",
    "humidity_threshold": 55.0
  }'
```

### Lấy trạng thái hiện tại

```bash
curl http://localhost:5000/api/status
```

### Gửi lệnh điều khiển

```bash
curl -X POST http://localhost:5000/api/command \
  -H "Content-Type: application/json" \
  -d '{
    "command": "set_pump_mode",
    "params": {"mode": "auto"}
  }'
```

### Lấy lệnh chờ xử lý (device sẽ call)

```bash
curl http://localhost:5000/api/command
```

### Lấy lịch sử sensor (100 record gần nhất)

```bash
curl "http://localhost:5000/api/history?limit=100&offset=0"
```

## 🧪 Unit Tests

### Chạy tests

```bash
pytest backend/tests/test_device_service.py -q
```

### Test Coverage

- `test_save_device_data_updates_status_and_values`: Xác nhận data lưu vào DB
- `test_queue_and_pop_pending_command`: Xác nhận lệnh được queue/pop đúng

## 🐳 Docker

### Build image

```bash
docker build -t yolobit-backend:latest .
```

### Run container

```bash
docker run -d -p 5000:5000 --name yolobit-backend yolobit-backend:latest
```

## 📚 Các File Quan Trọng

### `backend/app.py`
- FastAPI app khởi tạo
- Route `/` trả HTML dashboard (lấy từ `frontend/index.html`)
- CORS middleware
- Include device router

### `backend/api/routers/device.py`
- Tất cả API endpoints
- Request validation (Pydantic)
- Response serialization

### `backend/api/services/device_service.py`
- Business logic layer
- Lưu dữ liệu qua repository
- Queue command
- Lấy history

### `backend/api/repositories/memory_repository.py`
- Cache trạng thái hiện tại trong dict
- Lưu dữ liệu mới vào DB
- Lấy lịch sử từ DB
- Quản lý pending command

### `backend/db/db_manager.py`
- Khởi tạo SQLite DB
- CREATE TABLE nếu chưa tồn tại
- INSERT vào SensorHistory
- SELECT history với phân trang
- WAL mode + index setup

### `backend/core/dependencies.py`
- DI: tạo DBManager
- DI: tạo Repository
- DI: tạo Service
- FastAPI dependency provider

## 🔄 Data Flow

```
1. Yolobit gửi POST /api/data
   ↓
2. Router.receive_device_data() -> Service.save_device_data()
   ↓
3. Service gọi Repository.save_device_data()
   ↓
4. Repository gọi DBManager.insert_sensor_history()
   ↓
5. SQLite lưu vào SensorHistory table
   ↓
6. Repository cập nhật cache dict
   ↓
7. Response {"status": "ok"}

---

1. Web frontend call GET /api/status
   ↓
2. Router.get_device_status() -> Service.get_current_status()
   ↓
3. Service gọi Repository.get_device_status()
   ↓
4. Repository trả cache dict
   ↓
5. Response DeviceStatus JSON

---

1. Web frontend call GET /api/history?limit=100&offset=0
   ↓
2. Router.get_sensor_history() -> Service.get_sensor_history()
   ↓
3. Service gọi Repository.get_sensor_history()
   ↓
4. Repository gọi DBManager.get_sensor_history()
   ↓
5. SQLite query SensorHistory ORDER BY timestamp DESC
   ↓
6. Response SensorHistoryResponse JSON (100 records)
```

## 🚨 Troubleshooting

### Port 5000 đã bị dùng

```bash
# Tìm process dùng port 5000
# Windows
netstat -ano | findstr :5000

# macOS/Linux
lsof -i :5000

# Chạy ở port khác
uvicorn backend.app:app --port 5001
```

### Database file không thấy

```bash
# Kiểm tra file iot_data.db có tồn tại ở root project không
ls -la iot_data.db

# Nếu không, nó sẽ tự tạo khi có POST /api/data đầu tiên
```

### Lỗi `frontend/index.html` không tìm thấy

```
Lỗi: "Dashboard not found"
Giải pháp: Đảm bảo frontend/index.html tồn tại trong project root
```

## 📖 Tài Liệu Liên Quan

- **Frontend**: [frontend/README.md](../frontend/README.md)
- **Main Project**: [README.md](../README.md)
- **Pump Control**: [PUMP_QUICK_START.md](../PUMP_QUICK_START.md)
- **Webserver Setup**: [WEBSERVER_SETUP_GUIDE.md](../WEBSERVER_SETUP_GUIDE.md)

## 📝 Ghi Chú

- Backend chỉ cung cấp API, không xử lý logic điều khiển pump (đó là việc của Yolobit device)
- Tất cả dữ liệu lưu trong SQLite, không có cleanup automation (hãy thiết lập routine cleanup nếu cần)
- Frontend được phục vụ từ backend ở route `/` để tiện lợi, có thể tách ra serve riêng nếu muốn

## ✨ Kế Tiếp

Có thể mở rộng:
1. **Thêm authentication**: JWT token cho API protection
2. **Thêm timezone support**: Hiện tại dùng Unix timestamp, có thể thêm timezone aware timestamps
3. **Thêm data export**: CSV/Excel export từ lịch sử
4. **Thêm data analytics**: Tính average, min, max per time period
5. **Thêm alert**: Gửi email/SMS khi có anomaly
6. **Thêm caching**: Redis cache cho frequently accessed data
