# 🔐 AI Guardian.

## 📌 Overview

AI Guardian is an advanced AI-powered surveillance and monitoring system designed to enhance safety through real-time object detection and analysis. The system leverages deep learning and computer vision techniques to process live or recorded video feeds and identify potential threats.

Built using the YOLOv8 model, AI Guardian provides fast and accurate detection, making it suitable for smart surveillance, security monitoring, and automated threat detection applications.

---

## 🚀 Features

* Real-time object detection using YOLOv8
* Supports both live camera feed and static images
* Fast and efficient processing
* Deep learning-based threat identification
* User-friendly interface

---

## 🏗️ System Architecture

The system follows a modular architecture:

Frontend → Backend → AI Model (YOLOv8)

* **Frontend:** Handles user interaction and input
* **Backend:** Processes requests and communicates with the model
* **AI Model:** Performs object detection and returns results

---

## 🛠️ Tech Stack

* **Frontend:** HTML, CSS, JavaScript.
* **Backend:** Python.
* **Frameworks/Libraries:** OpenCV, NumPy, PyTorch.
* **Model:** YOLOv8 (Ultralytics).

---

## 📂 Project Structure

```
ai-guardian/
│
├── frontend/        # User interface
├── backend/         # Server and processing logic
├── yolov8n.pt       # Pre-trained model
├── test_frame.jpg   # Sample input
└── README.md
```

---

## ⚙️ Installation & Setup

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/ai-guardian.git

# Navigate to project folder
cd ai-guardian

# Install dependencies
pip install -r requirements.txt

# Run the backend
python app.py
```

---

## ▶️ Usage

1. Start the backend server
2. Open the frontend in a browser
3. Upload an image or enable camera feed
4. View real-time detection results

---

## 📊 Applications

* Smart surveillance systems
* Security monitoring
* Threat detection in restricted areas
* Automated safety systems

---

## 🔮 Future Enhancements

* Real-time alert system (SMS/Email)
* Cloud deployment
* Mobile application integration
* Advanced anomaly detection

---

