import requests
import time

alerts = [
    {"camera_id": "CAM-01", "event_type": "fire",     "confidence": 0.94},
    {"camera_id": "CAM-02", "event_type": "fall",     "confidence": 0.87},
    {"camera_id": "CAM-04", "event_type": "accident", "confidence": 0.81},
    {"camera_id": "CAM-01", "event_type": "crowd",    "confidence": 0.71},
]

print("Sending demo alerts...")
for alert in alerts:
    try:
        r = requests.post("http://localhost:8000/api/test-alert", json=alert)
        print(f"Sent: {alert['event_type']} on {alert['camera_id']}")
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(3)

print("Done! Check your dashboard.")