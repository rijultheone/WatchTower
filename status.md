to run file use: python webcam_gui.py


# Project Status – Webcam Monitoring Utility with GUI

**Date:** 20-07-2025

## Overview
Desktop application that opens the laptop webcam, detects motion or human faces, and automatically records clips that include a programmable lead-in (pre-buffer) and tail (post-buffer). All major settings are accessible through a Tkinter GUI.

## Tools & Technologies
- **Python 3.x** – core language
- **OpenCV (`opencv-python`)** – video capture, background subtraction, face detection
- **NumPy** – array operations
- **Tkinter** – native GUI toolkit (bundled with Python)
- **Pillow (`PIL`)** – converts OpenCV frames to Tk images for display
- **Python `datetime`, `collections`** – timestamped filenames and ring-buffer for pre-recording

## Key Features as of:(12:33 20-07-2015)
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



## Recent Enhancements as of:(01:40 21-07-2015)
- Added full Tkinter GUI with live preview & controls.
- Adjustable pre/post recording buffers.
- Settings dialog + keyboard shortcut.
- Exposed camera index & detection thresholds.

## Potential Next Steps
- Memory-efficient disk-based ring buffer for large pre-buffers.
- Replace Haar cascade with deep-learning person detector.
- Timeline/log panel of detection events.
- Package as standalone executable (PyInstaller).

--------
## Latest Updates - as of (02:13 21-07-2015)(post-GUI enhancements)
- **Detection List & Log**: A scrollable panel lists every recorded clip; double-click to open.  An "Export Log" button saves the list to CSV.
- **Custom Save Location**: Users can pick the destination directory in Settings.  Default is `Videos/SecCam`; the folder is created automatically if missing.
- **Master Recording**: "Always record" option (enabled by default) writes a continuous `master_YYYYMMDD_HHMMSS.avi` alongside event clips.  Each frame is timestamped.
- **Improved Overlays**: Faces are labeled "Human" on screen and in saved clips.
- **Playback Speed Fix**: Frame loop timing adjusted to eliminate fast-forward effect in recordings.

--------

## Additional Feature Ideas

5. **Performance & Quality**
   - Low-power mode: lower FPS until motion is detected.
6. **GUI Polish**
   - live FPS indicator.
   - First-run wizard for camera and folder setup.
   - Hotkeys: 
      - Space = Start, Stop 
      - Esc = Quit.
      - Q - Quit the application (already added)
      - d - Toggle debug mode (show confidence, FPS, etc.)  
      - Ctrl + F - Fullscreen mode for camera feed
      - Ctrl + B - blackout screen or run in background
     
7. **Packaging & Deployment**
   - One-click Windows installer (PyInstaller + NSIS).
   - Auto-update check via GitHub releases.
   - Headless “service” mode with local web dashboard.
8. **Cloud / Remote Access**
   - Upload finished clips to S3 or Google Drive.
   - Built-in MJPEG/live streaming server.
9. **Privacy & Security**
   - Optional face blur before saving.
   - Password-protected settings dialog.
   - Encryption of recorded clips.
10. **Tests & Analytics**
    - Unit tests on prerecorded footage.
    - Stats page plotting motion counts per hour/day.



