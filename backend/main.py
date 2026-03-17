import asyncio
import json
import cv2
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from datetime import datetime
import sqlite3

from detector import EmergencyDetector, DetectionEvent

app = FastAPI(title="AI Guardian API")

app.add_middleware(CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

os.makedirs("backend/clips", exist_ok=True)
app.mount("/clips", StaticFiles(directory="backend/clips"), name="clips")

# Database setup
def get_db():
    conn = sqlite3.connect("backend/guardian.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            camera_id TEXT,
            event_type TEXT,
            confidence REAL,
            clip_path TEXT,
            timestamp TEXT,
            bbox TEXT,
            acknowledged INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

init_db()

detector = EmergencyDetector()
ws_clients: list[WebSocket] = []
camera_tasks = {}

async def broadcast(data: dict):
    dead = []
    for ws in ws_clients:
        try:
            await ws.send_json(data)
        except:
            dead.append(ws)
    for d in dead:
        ws_clients.remove(d)

async def process_event(event: DetectionEvent):
    conn = get_db()
    cursor = conn.execute(
        """INSERT INTO events (camera_id, event_type, confidence, clip_path, timestamp, bbox)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (event.camera_id, event.event_type, event.confidence,
         event.clip_path, event.timestamp.isoformat(), json.dumps(event.bbox))
    )
    event_id = cursor.lastrowid
    conn.commit()
    conn.close()

    await broadcast({
        "type": "alert",
        "data": {
            "id": event_id,
            "camera_id": event.camera_id,
            "event_type": event.event_type,
            "confidence": event.confidence,
            "clip_path": event.clip_path,
            "timestamp": event.timestamp.isoformat(),
            "bbox": event.bbox
        }
    })

async def camera_worker(camera_id: str, source, backend=cv2.CAP_DSHOW):
    cap = cv2.VideoCapture(source, backend)
    if not cap.isOpened():
        print(f"ERROR: Could not open camera {source}")
        return
    loop = asyncio.get_event_loop()
    while True:
        ret, frame = await loop.run_in_executor(None, cap.read)
        if not ret:
            await asyncio.sleep(0.1)
            continue
        detector.buffer_frame(camera_id, frame)
        events = await loop.run_in_executor(None, detector.detect, frame, camera_id)
        for event in events:
            await process_event(event)
        await asyncio.sleep(0.033)

@app.on_event("startup")
async def startup():
    # Use webcam (0) for demo - change to video file path for testing
    asyncio.create_task(camera_worker("CAM-01", 0, cv2.CAP_DSHOW))

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    ws_clients.append(ws)
    print(f"Dashboard connected! Total clients: {len(ws_clients)}")
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        ws_clients.remove(ws)

@app.get("/api/events")
async def get_events(limit: int = 50):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM events ORDER BY timestamp DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/api/events/{event_id}/acknowledge")
async def acknowledge(event_id: int):
    conn = get_db()
    conn.execute("UPDATE events SET acknowledged=1 WHERE id=?", (event_id,))
    conn.commit()
    conn.close()
    return {"status": "ok"}

@app.get("/api/status")
async def status():
    return {"status": "running", "cameras": list(camera_tasks.keys())}
@app.post("/api/test-alert")
async def test_alert(data: dict):
    from datetime import datetime
    event = DetectionEvent(
        camera_id=data["camera_id"],
        event_type=data["event_type"],
        confidence=data["confidence"],
        bbox=[100, 100, 300, 300],
        frame=None,
        timestamp=datetime.utcnow()
    )
    await process_event(event)
    return {"status": "alert sent"}