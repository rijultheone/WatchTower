# Project Status – Webcam Monitoring Utility with GUI

**Date:** 2025-07-20

## Overview
Desktop application that opens the laptop webcam, detects motion or human faces, and automatically records clips that include a programmable lead-in (pre-buffer) and tail (post-buffer). All major settings are accessible through a Tkinter GUI.

## Tools & Technologies
- **Python 3.x** – core language
- **OpenCV (`opencv-python`)** – video capture, background subtraction, face detection
- **NumPy** – array operations
- **Tkinter** – native GUI toolkit (bundled with Python)
- **Pillow (`PIL`)** – converts OpenCV frames to Tk images for display
- **Python `datetime`, `collections`** – timestamped filenames and ring-buffer for pre-recording

## Key Features
1. **Graphical Interface (Tkinter)**
   • Live video preview inside main window.  
   • Control row with **Start · Stop · Settings** buttons.  
   • Global keyboard shortcut **S** to open Settings.
2. **Detection Logic**
   • **Face Detection** via Haar cascade (`haarcascade_frontalface_default.xml`).  
   • **Motion Detection** via MOG2 background subtractor + contour filtering.  
   • Overlays: red “Motion/Human Detected” text, blue face boxes, green motion boxes.
3. **Smart Recording**
   • Saves **N seconds BEFORE** the first detection (default 35 s) using an in-memory frame buffer.  
   • Records while activity persists and **M seconds AFTER** the last detection (default 15 s).  
   • Clips saved as `recording_YYYYMMDD_HHMMSS.avi` (XVID, original resolution/FPS).
4. **Settings Dialog**
   • Camera index.  
   • Minimum motion area (noise threshold).  
   • Pre-record buffer seconds.  
   • Post-record buffer seconds.  
   • Bound to live variables; adjust before pressing **Start** for next session.
5. **User Controls**
   • **Start / Stop** buttons control capture loop.  
   • **q** key inside preview still exits safely.

## Configurable Parameters (`webcam_gui.py`)
| GUI Field | Variable | Purpose | Default |
|-----------|----------|---------|---------|
| Pre-record buffer (s) | `pre_buffer_var` | Seconds cached before first detection | 35 |
| Post-record buffer (s) | `post_buffer_var` | Seconds to keep recording after silence | 15 |
| Min motion area | `min_area_var` | Contour area threshold (px²) | 5000 |
| Camera index | `cam_index_var` | Select webcam device | 0 |

## File Structure
```
webcam_feed.py   # Legacy console-only script
webcam_gui.py    # Current GUI application – use this one
status.md        # Project report (this file)
recording_*.avi  # Auto-generated video clips
```

## Setup & Usage
1. Install dependencies:
   ```bash
   pip install opencv-python numpy pillow
   ```
2. Run the GUI application:
   ```bash
   python webcam_gui.py
   ```
3. Adjust parameters → **Start**.  Press **S** for Settings, **Stop** to halt, **q** to quit.

## Recent Enhancements
- Added full Tkinter GUI with live preview & controls.
- Adjustable pre/post recording buffers.
- Settings dialog + keyboard shortcut.
- Exposed camera index & detection thresholds.

## Potential Next Steps
- Memory-efficient disk-based ring buffer for large pre-buffers.
- Replace Haar cascade with deep-learning person detector.
- Timeline/log panel of detection events.
- Package as standalone executable (PyInstaller).

---
*Prepared for client review.*

--------

## Additional Feature Ideas
1. **Detection Accuracy & Intelligence**
   - Replace Haar cascades with YOLOv8-n, MobileNet-SSD, or Mediapipe for fewer false positives.
   - User-defined mask zones to ignore TVs, windows, etc.
   - Optional sound detection (loud bang/clap) to trigger recording.
2. **Notifications & Evidence**
   - Save a JPEG snapshot whenever a clip starts.
   - Push alerts via e-mail, Telegram, Slack, or Windows toast.
   - Auto-cleanup: delete clips older than X days or based on free disk.
3. **Multi-Camera Support**
   - Tabs/drop-down to preview multiple cameras simultaneously.
   - Independent settings per camera and unified event timeline.
4. **Timeline / Log Panel**
   - Scrollable list of detections with double-click to open clip.
   - Exportable CSV log.
5. **Performance & Quality**
   - GPU acceleration (cv2.cuda, TensorRT) when available.
   - Encode H.264 with FFmpeg for smaller files.
   - Low-power mode: lower FPS until motion is detected.
6. **GUI Polish**
   - Dark-mode toggle and live FPS indicator.
   - First-run wizard for camera and folder setup.
   - Hotkeys: Space = Start/Stop, Esc = Quit.
7. **Packaging & Deployment**
   - One-click Windows installer (PyInstaller + NSIS).
   - Auto-update check via GitHub releases.
   - Headless “service” mode with local web dashboard.
8. **Cloud / Remote Access**
   - Upload finished clips to S3 or Google Drive.
   - Built-in MJPEG/live streaming server.
   - MQTT events for smart-home integration.
9. **Privacy & Security**
   - Optional face blur before saving.
   - Password-protected settings dialog.
   - Encryption of recorded clips.
10. **Tests & Analytics**
    - Unit tests on prerecorded footage.
    - Stats page plotting motion counts per hour/day.

to run file use: python webcam_gui.py