# 🖐️ Hand Gesture Media Controller

A real-time hand gesture recognition system that controls media playback (Play, Pause, Next, Previous, Volume) using just a webcam — no extra hardware required. Built with **Python, OpenCV, and MediaPipe**.

## 🎬 Demo

*(Add your demo GIF/video link here after uploading, e.g. a YouTube link or a GIF in this repo)*

## ✨ Features

- Real-time hand tracking using MediaPipe's 21-point hand landmark model
- Gesture stability buffer (majority voting across frames) for accurate, flicker-free detection
- Pinch gesture (thumb + index finger) for smooth, continuous volume control with a live on-screen volume bar
- Professional UI overlay — gesture status, last action, cooldown indicator, live FPS counter
- Startup splash screen with gesture guide
- No additional hardware needed — works with any standard webcam

## 🎯 Gestures

| Gesture | Action |
|---|---|
| ✋ Open Palm | Play |
| ✊ Fist | Pause |
| ☝️ Index Finger Up | Next Track |
| ✌️ Peace Sign | Previous Track |
| 🤏 Pinch (Thumb + Index) | Continuous Volume Control |

## 🛠️ Tech Stack

- **Python 3.10 / 3.11**
- **OpenCV** — webcam capture, frame processing, UI rendering
- **MediaPipe** — hand landmark detection and tracking
- **PyAutoGUI** — simulating system media key presses

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or 3.11 installed
- A working webcam

### Installation

```bash
git clone https://github.com/MohammadSohail09/hand-gesture-media-controller.git
cd hand-gesture-media-controller
pip install -r requirements.txt
```

### Run

```bash
python gesture_media_controller_v3.py
```

Press any key at the splash screen to start, show gestures to the camera, and press `q` to quit.

## 📁 Project Structure

```
├── gesture_media_controller_v3.py   # Main application (latest version)
├── requirements.txt                 # Python dependencies
└── README.md
```

## 🧠 How It Works

1. OpenCV captures live frames from the webcam
2. MediaPipe processes each frame and returns 21 hand landmark coordinates
3. A gesture classifier checks finger positions (up/down, pinch distance) to identify the current gesture
4. A rolling buffer of recent frames is used to confirm a gesture only when it's stable — this filters out false positives from hand jitter
5. Once confirmed, the corresponding system media key is triggered via PyAutoGUI

## 🔮 Future Improvements

- Multi-hand gesture support
- Custom gesture training/configuration
- Cross-platform system volume control via native OS APIs

## 👤 Author

**Mohammad Sohail**
B.Tech CSE, Siwan College of Engineering and Management (Bihar Engineering University)
[GitHub](https://github.com/MohammadSohail09) · [LinkedIn](https://www.linkedin.com/in/mohammad-sohail-5963b9327)

## 📄 License

This project is open source and available for learning purposes.
