"""Configuration handling module."""

import json
from pathlib import Path
from typing import Dict, Any, Optional

class Config:
    def __init__(self, config_file: str = "~/.watchtower_config.json"):
        self.config_file = Path(config_file).expanduser()
        self.config: Dict[str, Any] = self._load_default_config()
        
        if self.config_file.exists():
            self._load_config()

    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration."""
        return {
            "camera_index": 0,
            "output_folder": str(Path.home() / "Videos" / "SecCam"),
            "min_motion_area": 5000,
            "pre_buffer_seconds": 10,
            "post_buffer_seconds": 10,
            "always_record": True,
            "debug_mode": False,
            "fullscreen": False,
            "background_mode": False
        }

    def _load_config(self) -> None:
        """Load configuration from file."""
        try:
            with open(self.config_file, "r") as f:
                loaded_config = json.load(f)
                # Update config with loaded values, keeping defaults for missing keys
                self.config.update(loaded_config)
        except Exception as e:
            print(f"Error loading config: {e}")

    def save(self) -> bool:
        """Save current configuration to file."""
        try:
            # Ensure parent directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save config
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config[key] = value

    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple configuration values."""
        self.config.update(updates)

    @property
    def camera_index(self) -> int:
        """Get camera index."""
        return self.get("camera_index", 0)

    @camera_index.setter
    def camera_index(self, value: int) -> None:
        """Set camera index."""
        self.set("camera_index", value)

    @property
    def output_folder(self) -> str:
        """Get output folder."""
        return self.get("output_folder", str(Path.home() / "Videos" / "SecCam"))

    @output_folder.setter
    def output_folder(self, value: str) -> None:
        """Set output folder."""
        self.set("output_folder", value)

    @property
    def min_motion_area(self) -> int:
        """Get minimum motion area."""
        return self.get("min_motion_area", 5000)

    @min_motion_area.setter
    def min_motion_area(self, value: int) -> None:
        """Set minimum motion area."""
        self.set("min_motion_area", value)

    @property
    def pre_buffer_seconds(self) -> int:
        """Get pre-buffer duration in seconds."""
        return self.get("pre_buffer_seconds", 10)

    @pre_buffer_seconds.setter
    def pre_buffer_seconds(self, value: int) -> None:
        """Set pre-buffer duration in seconds."""
        self.set("pre_buffer_seconds", value)

    @property
    def post_buffer_seconds(self) -> int:
        """Get post-buffer duration in seconds."""
        return self.get("post_buffer_seconds", 10)

    @post_buffer_seconds.setter
    def post_buffer_seconds(self, value: int) -> None:
        """Set post-buffer duration in seconds."""
        self.set("post_buffer_seconds", value)

    @property
    def always_record(self) -> bool:
        """Get always record setting."""
        return self.get("always_record", True)

    @always_record.setter
    def always_record(self, value: bool) -> None:
        """Set always record setting."""
        self.set("always_record", value)

    @property
    def debug_mode(self) -> bool:
        """Get debug mode setting."""
        return self.get("debug_mode", False)

    @debug_mode.setter
    def debug_mode(self, value: bool) -> None:
        """Set debug mode setting."""
        self.set("debug_mode", value)

    @property
    def fullscreen(self) -> bool:
        """Get fullscreen setting."""
        return self.get("fullscreen", False)

    @fullscreen.setter
    def fullscreen(self, value: bool) -> None:
        """Set fullscreen setting."""
        self.set("fullscreen", value)

    @property
    def background_mode(self) -> bool:
        """Get background mode setting."""
        return self.get("background_mode", False)

    @background_mode.setter
    def background_mode(self, value: bool) -> None:
        """Set background mode setting."""
        self.set("background_mode", value) 