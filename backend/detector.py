import cv2
import torch
import time
from ultralytics import YOLO
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque

@dataclass
class DetectionEvent:
    camera_id: str
    event_type: str
    confidence: float
    bbox: list
    frame: object
    timestamp: datetime = field(default_factory=datetime.utcnow)
    clip_path: str = None

class EmergencyDetector:
    LABELS = {
        "fire":     ["fire", "smoke"],
        "fall":     ["person"],
        "accident": ["car", "truck", "bus"],
        "crowd":    ["person"],
    }
    THRESHOLDS = {"fire": 0.40, "fall": 0.60, "accident": 0.55, "crowd": 0.50}
    COOLDOWN_SEC = 8

    def __init__(self, model_path="yolov8n.pt"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = YOLO(model_path)
        self._last_alert = {}
        self._clip_buffers = {}

    def _in_cooldown(self, camera_id, event_type):
        key = f"{camera_id}:{event_type}"
        last = self._last_alert.get(key, 0)
        if time.time() - last < self.COOLDOWN_SEC:
            return True
        self._last_alert[key] = time.time()
        return False

    def buffer_frame(self, camera_id, frame):
        if camera_id not in self._clip_buffers:
            self._clip_buffers[camera_id] = deque(maxlen=150)
        self._clip_buffers[camera_id].append(frame.copy())

    def save_clip(self, camera_id, event_type):
        import os
        os.makedirs("backend/clips", exist_ok=True)
        frames = list(self._clip_buffers.get(camera_id, []))
        if not frames:
            return None
        path = f"backend/clips/{camera_id}_{event_type}_{int(time.time())}.mp4"
        h, w = frames[0].shape[:2]
        writer = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"mp4v"), 20, (w, h))
        for f in frames:
            writer.write(f)
        writer.release()
        return path

    def detect(self, frame, camera_id):
        results = self.model(frame, verbose=False)[0]
        events = []
        class_names = self.model.names
        person_count = 0

        for box in results.boxes:
            cls_name = class_names[int(box.cls)].lower()
            conf = float(box.conf)
            bbox = box.xyxy[0].tolist()

            if "person" in cls_name:
                person_count += 1

            for event_type, keywords in self.LABELS.items():
                if any(k in cls_name for k in keywords):
                    threshold = self.THRESHOLDS[event_type]
                    if event_type == "crowd" and person_count < 4:
                        continue
                    if conf >= threshold and not self._in_cooldown(camera_id, event_type):
                        clip_path = self.save_clip(camera_id, event_type)
                        events.append(DetectionEvent(
                            camera_id=camera_id,
                            event_type=event_type,
                            confidence=round(conf, 3),
                            bbox=bbox,
                            frame=frame.copy(),
                            clip_path=clip_path
                        ))
        return events