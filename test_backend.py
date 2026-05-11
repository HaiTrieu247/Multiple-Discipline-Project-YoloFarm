"""
test_backend.py -- Kiem tra toan bo pipeline: backend API + SQLite
Chay: python test_backend.py
Backend phai dang chay (uvicorn backend.app:app --port 5000)
"""

import json
import sqlite3
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = "http://localhost:5000"
DB_PATH = Path(__file__).parent / "iot_data.db"


def _get(path):
    try:
        with urllib.request.urlopen(f"{BASE}{path}", timeout=5) as r:
            return json.loads(r.read()), r.status
    except urllib.error.URLError as e:
        return None, str(e)


def _post(path, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return json.loads(r.read()), r.status
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return {"error": body}, e.code
    except urllib.error.URLError as e:
        return None, str(e)


def ok(msg):
    print(f"  [OK]  {msg}")


def fail(msg):
    print(f"  [FAIL] {msg}")


def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# --- Buoc 1: kiem tra server dang chay ---

section("BUOC 1 -- Server co dang chay khong?")
body, status = _get("/api/status")
if body is None:
    fail(f"Khong ket noi duoc toi {BASE}  -->  {status}")
    fail("Hay chay:  uvicorn backend.app:app --reload --port 5000")
    raise SystemExit(1)
ok(f"Server phan hoi  (HTTP {status})")
print(f"       /api/status hien tai:")
for k, v in body.items():
    print(f"         {k:25s}: {v}")

# --- Buoc 2: POST du lieu gia (mo phong board) ---

section("BUOC 2 -- POST du lieu gia (mo phong board gui len)")
fake = {
    "timestamp": time.time(),
    "temperature": 27.3,
    "humidity": 62.5,
    "soil_moisture": 45,
    "light_level": 1800,
    "pump_state": 0,
    "pump_mode": "auto",
    "humidity_threshold": 55.0,
}
body, status = _post("/api/data", fake)
if status == 200 and body == {"status": "ok"}:
    ok(f"POST /api/data  -->  {body}")
else:
    fail(f"POST /api/data that bai (HTTP {status}): {body}")
    raise SystemExit(1)

# --- Buoc 3: doc lai /api/status ---

section("BUOC 3 -- Doc lai /api/status (phai thay data vua POST)")
time.sleep(0.3)
body, status = _get("/api/status")
temp = body.get("temperature") if body else None
if temp is not None and abs(temp - fake["temperature"]) < 0.01:
    ok(f"/api/status.temperature = {temp}  -- khop!")
else:
    fail(f"/api/status.temperature = {temp}  (mong doi {fake['temperature']})")
if body:
    print("       status day du:")
    for k, v in body.items():
        print(f"         {k:25s}: {v}")

# --- Buoc 4: doc /api/history ---

section("BUOC 4 -- Doc /api/history (phai co it nhat 1 record)")
body, status = _get("/api/history?limit=5&offset=0")
if body is None or status != 200:
    fail(f"GET /api/history that bai: {body}")
else:
    total = body.get("total", 0)
    records = body.get("records", [])
    ok(f"Tong {total} record trong DB, tra ve {len(records)} record")
    if records:
        latest = records[0]
        print("       Record moi nhat:")
        for k, v in latest.items():
            print(f"         {k:25s}: {v}")
    else:
        fail("Khong co record nao -- DB co the chua duoc ghi")

# --- Buoc 5: kiem tra file SQLite truc tiep ---

section("BUOC 5 -- Kiem tra file SQLite truc tiep")
if not DB_PATH.exists():
    fail(f"File {DB_PATH} KHONG ton tai!")
else:
    ok(f"File ton tai: {DB_PATH}  ({DB_PATH.stat().st_size} bytes)")
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    count = conn.execute("SELECT COUNT(*) as n FROM SensorHistory").fetchone()["n"]
    ok(f"SensorHistory co {count} record")
    if count:
        row = dict(conn.execute(
            "SELECT * FROM SensorHistory ORDER BY timestamp DESC LIMIT 1"
        ).fetchone())
        print("       Record moi nhat trong DB:")
        for k, v in row.items():
            print(f"         {k:25s}: {v}")
    conn.close()

# --- Buoc 6: kiem tra IP laptop ---

section("BUOC 6 -- IP cua laptop (board phai dung IP nay)")
import socket
hostname = socket.gethostname()
try:
    ip = socket.gethostbyname(hostname)
except Exception:
    ip = "khong xac dinh"
print(f"       Hostname : {hostname}")
print(f"       IP       : {ip}")
print()
print("  >> Mo micropython/config.py va dam bao:")
print(f"       WEBSERVER_IP = \"{ip}\"")
print()

# Kiem tra config.py tren board
config_path = Path(__file__).parent / "micropython" / "config.py"
if config_path.exists():
    content = config_path.read_text(encoding="utf-8")
    import re
    m = re.search(r'WEBSERVER_IP\s*=\s*["\'](.+?)["\']', content)
    if m:
        board_ip = m.group(1)
        if board_ip == ip:
            ok(f"config.py WEBSERVER_IP = \"{board_ip}\"  -- dung!")
        else:
            fail(f"config.py WEBSERVER_IP = \"{board_ip}\"  -- SAI! Phai la \"{ip}\"")
            print(f"       --> Sua micropython/config.py: WEBSERVER_IP = \"{ip}\"")

print(f"\n{'='*60}")
print("  Xong. Neu tat ca OK --> backend hoat dong dung.")
print("  Neu co FAIL --> xem ghi chu phia tren de sua.")
print(f"{'='*60}\n")
