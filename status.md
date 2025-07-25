# WatchTower - Smart Webcam Monitoring System

## Quick Start
```bash
# OR
python -m watchtower.main
```

## Overview
WatchTower is a desktop application that provides intelligent webcam monitoring with motion and face detection capabilities. It automatically records events with configurable pre and post-event buffering.

## Core Features

### 📹 Video Monitoring
- Real-time webcam feed display
- Motion detection with adjustable sensitivity
- Face detection using Haar cascade
- Visual overlays for detected events
- Continuous master recording option

### 🎥 Smart Recording
- Pre-event buffer (default: 35s)
- Post-event buffer (default: 15s)
- Automatic clip generation on detection
- Timestamped file naming: `recording_YYYYMMDD_HHMMSS.avi`

### 🖥️ User Interface
- Modern Tkinter-based GUI
- Live video preview
- Detection event log with playback
- Customizable settings panel
- Keyboard shortcuts for quick control

## Keyboard Shortcuts
| Key         | Action                    |
|-------------|---------------------------|
| Space       | Start/Stop monitoring     |
| S           | Open Settings             |
| Q           | Quit application          |
| D           | Toggle debug overlay      |
| Ctrl + F    | Toggle fullscreen         |
| Ctrl + B    | Background mode           |
| Esc         | Exit fullscreen           |

## Technical Stack
- Python 3.x
- OpenCV (opencv-python)
- NumPy
- Tkinter
- Pillow (PIL)

## Configuration
Access settings through:
1. Settings button in main window
2. 'S' keyboard shortcut

Adjustable parameters:
- Camera selection
- Motion sensitivity
- Buffer durations
- Save location
- Recording options

## Roadmap
- [ ] Deep learning-based person detection
- [ ] Cloud storage integration
- [ ] Remote access dashboard
- [ ] Encrypted storage
- [ ] Face anonymization
- [ ] Performance analytics

## Development Status
Last updated: 2025-07-21

Current focus:
- Performance optimization
- GUI polish
- Automated testing
- Deployment packaging



