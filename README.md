# Watch Tower

A powerful desktop security application that uses your webcam for real-time monitoring with automatic recording when motion or humans are detected.

## Features

- Motion detection using background subtraction
- Face detection
- Pre/post recording buffer
- Automatic clip saving
- Export capabilities
- Background operation mode
- User-friendly GUI with live preview

## Requirements

- Python 3.7 or higher
- OpenCV
- NumPy
- Pillow (PIL)
- Tkinter (usually comes with Python)

## Installation

### From Source

1. Clone the repository:
```bash
git clone https://github.com/yourusername/watchtower.git
cd watchtower
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package:
```bash
pip install -e .
```

### Using pip

```bash
pip install watchtower
```

## Usage

1. Start the application:
```bash
watchtower
```

2. On first run, the setup wizard will help you configure:
   - Camera selection
   - Storage location
   - Basic settings

3. Use the GUI or keyboard shortcuts to control the application:
   - Space: Start/Stop recording
   - Esc: Close current window
   - Q: Quit application
   - D: Toggle debug overlay
   - Ctrl + F: Toggle fullscreen
   - Ctrl + B: Run in background
   - S: Open settings

## Project Structure

```
watchtower/
├── watchtower/
│   ├── __init__.py
│   ├── main.py
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   ├── wizard.py
│   │   └── settings.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── camera.py
│   │   ├── detection.py
│   │   └── recording.py
│   └── utils/
│       ├── __init__.py
│       ├── config.py
│       └── video.py
├── setup.py
├── README.md
└── requirements.txt
```

## Configuration

The application stores its configuration in `~/.watchtower_config.json`. You can modify this file directly or use the settings dialog in the application.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenCV team for the computer vision library
- Python community for the excellent tools and libraries 