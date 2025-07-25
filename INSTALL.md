# WatchTower Installation Guide

## Prerequisites

- Python 3.x (3.7 or newer recommended)
- pip (Python package installer)
- Webcam connected to your system
- Git (optional, for cloning the repository)

## System Requirements

- Operating System: Windows 10/11, macOS, or Linux
- RAM: 2GB minimum (4GB recommended)
- Storage: 100MB for installation + space for recordings
- Webcam: Any USB webcam or built-in laptop camera

## Installation Methods

### Method 1: Direct Installation (Recommended)

1. Clone or download the repository:
   ```bash
   git clone <repository-url>
   # OR
   # Download and extract the ZIP file
   ```

2. Navigate to the project directory:
   ```bash
   cd watchtower
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

### Method 2: Manual Installation

1. Ensure you have all dependencies:
   ```bash
   pip install opencv-python>=4.5.0
   pip install numpy>=1.19.0
   pip install pillow>=8.0.0
   ```

2. Copy the project files to your desired location

3. Run the application directly:
   ```bash
   python webcam_gui.py
   # OR
   python -m watchtower.main
   ```

## Configuration

### Default Settings
- Recordings save location: `C:\Users\<YourUsername>\WatchTower\Recordings`
- Pre-buffer time: 10 seconds
- Post-buffer time: 10 seconds
- Motion detection sensitivity: Medium

### Changing Settings
1. Press 'S' while the application is running to open Settings
2. Or edit `~/.watchtower_config.json` directly (created after first run)

## Uninstallation

### Method 1: Using pip
```bash
pip uninstall watchtower
```

### Method 2: Manual Cleanup
1. Uninstall using pip
2. Delete the project directory
3. Remove configuration file:
   ```bash
   # Windows
   del %USERPROFILE%\.watchtower_config.json
   
   # Linux/macOS
   rm ~/.watchtower_config.json
   ```
4. Remove recordings directory (optional):
   ```bash
   # Windows
   rd /s /q %USERPROFILE%\WatchTower
   
   # Linux/macOS
   rm -rf ~/WatchTower
   ```

## Troubleshooting

### Common Issues

1. **Camera Not Found**
   - Ensure your webcam is properly connected
   - Try a different USB port
   - Check if other applications are using the camera

2. **Installation Fails**
   - Upgrade pip: `pip install --upgrade pip`
   - Install wheel: `pip install wheel`
   - Try installing dependencies separately

3. **Recording Directory Issues**
   - Ensure you have write permissions
   - Check available disk space
   - Try creating the directory manually

### Getting Help

If you encounter any issues:
1. Check the console output for error messages
2. Verify your Python version: `python --version`
3. Check installed dependencies: `pip freeze`
4. Submit an issue on the project repository

## Updating

To update to the latest version:

1. Pull the latest changes:
   ```bash
   git pull origin main
   ```

2. Reinstall the package:
   ```bash
   pip install -e .
   ```

## Development Setup

For contributors and developers:

1. Create a virtual environment:
   ```bash
   python -m venv venv
   
   # Windows
   .\venv\Scripts\activate
   
   # Linux/macOS
   source venv/bin/activate
   ```

2. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install the package in editable mode:
   ```bash
   pip install -e .
   ``` 