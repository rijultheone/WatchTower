"""Settings dialog module."""

import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path

from ..utils.config import Config
from ..core.camera import Camera

class SettingsDialog:
    def __init__(self, parent: tk.Tk, config: Config):
        self.window = tk.Toplevel(parent)
        self.window.title("Settings")
        self.window.geometry("400x500")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()  # Make window modal
        
        # Center the window
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (parent.winfo_screenwidth() // 2) - (width // 2)
        y = (parent.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'+{x}+{y}')
        
        self.config = config
        self._create_widgets()
        
    def _create_widgets(self):
        """Create the settings dialog widgets."""
        # Camera settings
        camera_frame = ttk.LabelFrame(self.window, text="Camera Settings", padding=10)
        camera_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(camera_frame, text="Camera:").grid(row=0, column=0, sticky="w")
        self.camera_combo = ttk.Combobox(camera_frame, width=30, state="readonly")
        self.camera_combo.grid(row=0, column=1, padx=5)
        ttk.Button(camera_frame, text="Refresh",
                  command=self._refresh_cameras).grid(row=0, column=2)
        
        # Detection settings
        detection_frame = ttk.LabelFrame(self.window, text="Detection Settings", padding=10)
        detection_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(detection_frame, text="Min motion area:").grid(row=0, column=0, sticky="w")
        self.motion_area = tk.StringVar(value=str(self.config.min_motion_area))
        ttk.Entry(detection_frame, textvariable=self.motion_area,
                 width=10).grid(row=0, column=1, padx=5)
        
        # Recording settings
        recording_frame = ttk.LabelFrame(self.window, text="Recording Settings", padding=10)
        recording_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(recording_frame, text="Pre-record buffer (s):").grid(row=0, column=0, sticky="w")
        self.pre_buffer = tk.StringVar(value=str(self.config.pre_buffer_seconds))
        ttk.Entry(recording_frame, textvariable=self.pre_buffer,
                width=5).grid(row=0, column=1, padx=5)
        
        ttk.Label(recording_frame, text="Post-record buffer (s):").grid(row=1, column=0, sticky="w")
        self.post_buffer = tk.StringVar(value=str(self.config.post_buffer_seconds))
        ttk.Entry(recording_frame, textvariable=self.post_buffer,
                width=5).grid(row=1, column=1, padx=5)
        
        # Storage settings
        storage_frame = ttk.LabelFrame(self.window, text="Storage Settings", padding=10)
        storage_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(storage_frame, text="Save recordings to:").grid(row=0, column=0, sticky="w")
        self.output_folder = tk.StringVar(value=self.config.output_folder)
        ttk.Entry(storage_frame, textvariable=self.output_folder,
                width=30).grid(row=0, column=1, padx=5)
        ttk.Button(storage_frame, text="Browse",
                  command=self._browse_folder).grid(row=0, column=2)
        
        # Options
        options_frame = ttk.LabelFrame(self.window, text="Options", padding=10)
        options_frame.pack(fill="x", padx=10, pady=5)
        
        self.always_record = tk.BooleanVar(value=self.config.always_record)
        ttk.Checkbutton(options_frame, text="Always record (master clip)",
                      variable=self.always_record).pack(anchor="w")
        
        self.debug_mode = tk.BooleanVar(value=self.config.debug_mode)
        ttk.Checkbutton(options_frame, text="Debug mode",
                      variable=self.debug_mode).pack(anchor="w")
        
        # Buttons
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Save",
                  command=self._save_settings).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Cancel",
                  command=self.window.destroy).pack(side="right", padx=5)
        
        # Initialize camera list
        self._refresh_cameras()
        
    def _refresh_cameras(self):
        """Refresh the list of available cameras."""
        cameras = []
        available_cameras = Camera.list_cameras()
        
        if not available_cameras:
            cameras = ["No cameras found"]
        else:
            cameras = [f"Camera {i}" for i in available_cameras]
        
        self.camera_combo['values'] = cameras
        
        # Select current camera
        current_camera = self.config.camera_index
        if current_camera < len(cameras) and cameras[0] != "No cameras found":
            self.camera_combo.current(current_camera)
            
    def _browse_folder(self):
        """Browse for output folder."""
        folder = filedialog.askdirectory(
            initialdir=self.output_folder.get(),
            title="Select Output Folder"
        )
        if folder:
            self.output_folder.set(folder)
            
    def _validate_settings(self) -> bool:
        """Validate settings before saving."""
        try:
            # Validate motion area
            motion_area = int(self.motion_area.get())
            if motion_area <= 0:
                raise ValueError("Motion area must be positive")
                
            # Validate buffers
            pre_buffer = int(self.pre_buffer.get())
            post_buffer = int(self.post_buffer.get())
            if pre_buffer < 0 or post_buffer < 0:
                raise ValueError("Buffer values must be non-negative")
                
            # Validate output folder
            output_path = Path(self.output_folder.get())
            if not output_path.is_absolute():
                raise ValueError("Output path must be absolute")
                
            # Try to create/access output folder
            output_path.mkdir(parents=True, exist_ok=True)
            
            return True
            
        except ValueError as e:
            tk.messagebox.showerror("Invalid Settings", str(e))
            return False
        except Exception as e:
            tk.messagebox.showerror("Error", f"Invalid settings:\n{str(e)}")
            return False
            
    def _save_settings(self):
        """Save settings and close dialog."""
        if not self._validate_settings():
            return
            
        # Update config
        if self.camera_combo.get() != "No cameras found":
            self.config.camera_index = int(self.camera_combo.get().split()[-1])
            
        self.config.min_motion_area = int(self.motion_area.get())
        self.config.pre_buffer_seconds = int(self.pre_buffer.get())
        self.config.post_buffer_seconds = int(self.post_buffer.get())
        self.config.output_folder = self.output_folder.get()
        self.config.always_record = self.always_record.get()
        self.config.debug_mode = self.debug_mode.get()
        
        # Save to file
        if self.config.save():
            self.window.destroy()
        else:
            tk.messagebox.showerror(
                "Error",
                "Failed to save settings. Please check file permissions."
            ) 