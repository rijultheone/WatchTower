import cv2
import numpy as np
import datetime
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
from PIL import Image, ImageTk  # pillow is required
import collections
import os
import platform
from pathlib import Path
import json


class FirstRunWizard:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("First-Time Setup Wizard")
        self.window.geometry("500x400")  # Smaller window
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()  # Make window modal
        
        # Center the window
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'+{x}+{y}')
        
        # Variables
        self.selected_camera = tk.IntVar(value=0)
        self.output_folder = tk.StringVar(value=str(Path.home() / "Videos" / "SecCam"))
        self.current_step = 0  # 0: Welcome, 1: Camera, 2: Storage, 3: Hotkeys
        
        # Result storage
        self.result = None
        
        # Create frames for each step
        self.frames = []
        self._create_welcome_page()
        self._create_camera_page()
        self._create_storage_page()
        self._create_hotkeys_page()
        
        # Navigation buttons frame
        self.nav_frame = ttk.Frame(self.window)
        self.nav_frame.pack(side="bottom", fill="x", padx=20, pady=10)
        
        self.back_btn = ttk.Button(self.nav_frame, text="Back", command=self._back_step)
        self.back_btn.pack(side="left")
        
        self.next_btn = ttk.Button(self.nav_frame, text="Next", command=self._next_step)
        self.next_btn.pack(side="right")
        
        # Show first step
        self._update_navigation()
        self.show_step(0)
        
    def _create_welcome_page(self):
        frame = ttk.Frame(self.window)
        
        # Step indicator
        ttk.Label(frame, text="Welcome", font=("", 12, "bold")).pack(pady=20)
        
        # Welcome text
        welcome_text = """Welcome to Webcam Monitor!

This wizard will help you set up:
• Your camera
• Storage location
• Keyboard shortcuts

Click Next to begin."""
        ttk.Label(frame, text=welcome_text, wraplength=400, justify="left").pack(padx=20, pady=20)
        
        self.frames.append(frame)
        
    def _create_camera_page(self):
        frame = ttk.Frame(self.window)
        
        # Step indicator
        ttk.Label(frame, text="Camera Setup", font=("", 12, "bold")).pack(pady=20)
        
        # Camera preview
        self.preview_label = ttk.Label(frame)
        self.preview_label.pack(pady=10)
        
        # Camera selector
        camera_select_frame = ttk.Frame(frame)
        camera_select_frame.pack(fill="x", padx=20)
        ttk.Label(camera_select_frame, text="Select Camera:").pack(side="left")
        self.camera_combo = ttk.Combobox(camera_select_frame, width=20, state="readonly")
        self.camera_combo.pack(side="left", padx=5)
        ttk.Button(camera_select_frame, text="Refresh", command=self._refresh_cameras).pack(side="left", padx=5)
        ttk.Button(camera_select_frame, text="Test", command=self._test_camera).pack(side="left", padx=5)
        
        self.frames.append(frame)
        
    def _create_storage_page(self):
        frame = ttk.Frame(self.window)
        
        # Step indicator
        ttk.Label(frame, text="Storage Location", font=("", 12, "bold")).pack(pady=20)
        
        # Storage location
        ttk.Label(frame, text="Choose where to save recordings:", wraplength=400).pack(padx=20, pady=10)
        
        folder_frame = ttk.Frame(frame)
        folder_frame.pack(fill="x", padx=20)
        self.folder_entry = ttk.Entry(folder_frame, textvariable=self.output_folder, width=30)
        self.folder_entry.pack(side="left", padx=5)
        ttk.Button(folder_frame, text="Browse...", command=self._browse_folder).pack(side="left", padx=5)
        
        # Folder validation message
        self.folder_validation = ttk.Label(frame, text="", foreground="red", wraplength=400)
        self.folder_validation.pack(fill="x", padx=20, pady=5)
        
        # Add folder validation on entry change
        self.output_folder.trace_add("write", lambda *args: self._validate_folder())
        
        self.frames.append(frame)
        
    def _create_hotkeys_page(self):
        frame = ttk.Frame(self.window)
        
        # Step indicator
        ttk.Label(frame, text="Keyboard Shortcuts", font=("", 12, "bold")).pack(pady=20)
        
        # Hotkeys information
        hotkeys_text = """Available shortcuts:

• Space - Start/Stop recording
• Esc - Close current window
• Q - Quit application
• D - Toggle debug overlay
• Ctrl + F - Toggle fullscreen
• Ctrl + B - Run in background
• S - Open settings"""
        
        ttk.Label(frame, text=hotkeys_text, justify="left").pack(padx=20)
        
        self.frames.append(frame)
        
    def show_step(self, step):
        """Show the specified step and hide others."""
        # Hide all frames
        for frame in self.frames:
            frame.pack_forget()
            
        # Show requested frame
        self.frames[step].pack(fill="both", expand=True)
        self.current_step = step
        
        # Start camera preview if on camera page
        if step == 1:  # Camera page
            self._refresh_cameras()
            self._start_camera_preview()
        else:
            # Stop camera preview if leaving camera page
            self.preview_running = False
            if hasattr(self, 'preview_cap') and self.preview_cap is not None:
                self.preview_cap.release()
                self.preview_cap = None
        
        self._update_navigation()
        
    def _update_navigation(self):
        """Update navigation button states."""
        # Update back button
        if self.current_step == 0:
            self.back_btn.config(state="disabled")
        else:
            self.back_btn.config(state="normal")
            
        # Update next button
        if self.current_step == len(self.frames) - 1:
            self.next_btn.config(text="Finish", command=self._on_save)
        else:
            self.next_btn.config(text="Next", command=self._next_step)
            
        # Disable next button on storage page if path is invalid
        if self.current_step == 2:  # Storage page
            if not self._validate_folder():
                self.next_btn.config(state="disabled")
            else:
                self.next_btn.config(state="normal")
        else:
            self.next_btn.config(state="normal")
        
    def _next_step(self):
        """Advance to the next step."""
        if self.current_step < len(self.frames) - 1:
            self.show_step(self.current_step + 1)
        
    def _back_step(self):
        """Go back to the previous step."""
        if self.current_step > 0:
            self.show_step(self.current_step - 1)

    def _refresh_cameras(self):
        """Refresh the list of available cameras."""
        cameras = []
        for i in range(5):  # Check first 5 possible cameras
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    cameras.append(f"Camera {i}")
                cap.release()
        
        if not cameras:
            cameras = ["No cameras found"]
            messagebox.showwarning("No Cameras", "No working cameras were detected.\nPlease connect a camera and click Refresh.")
        
        self.camera_combo['values'] = cameras
        if cameras[0] != "No cameras found":
            self.camera_combo.current(0)
            self.selected_camera.set(0)
            
    def _start_camera_preview(self):
        """Start the camera preview."""
        self.preview_running = True
        self.preview_cap = None
        self._update_preview()
        
    def _update_preview(self):
        """Update the camera preview frame."""
        if not self.preview_running:
            return
            
        if self.camera_combo.get().startswith("No cameras"):
            if self.preview_cap is not None:
                self.preview_cap.release()
                self.preview_cap = None
            self.preview_label.configure(image="")
            self.window.after(1000, self._update_preview)
            return
            
        try:
            if self.preview_cap is None:
                self.preview_cap = cv2.VideoCapture(self.selected_camera.get())
            
            ret, frame = self.preview_cap.read()
            if ret:
                # Resize frame to fit in the window
                frame = cv2.resize(frame, (320, 240))
                # Convert to RGB for PIL
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Convert to PhotoImage
                img = ImageTk.PhotoImage(Image.fromarray(frame_rgb))
                self.preview_label.imgtk = img
                self.preview_label.configure(image=img)
            
        except Exception as e:
            print(f"Preview error: {e}")
            
        self.window.after(33, self._update_preview)  # ~30 fps

    def _validate_folder(self):
        """Validate the output folder path and update UI accordingly."""
        folder = self.output_folder.get()
        try:
            path = Path(folder)
            # Check if path is absolute
            if not path.is_absolute():
                self.folder_validation.config(text="Please enter an absolute path")
                self.next_btn.config(state="disabled") # Disable next on invalid folder
                return False
                
            # Check if parent directory exists and is writable
            parent = path.parent
            if not parent.exists():
                self.folder_validation.config(text="Parent directory does not exist")
                self.next_btn.config(state="disabled") # Disable next on invalid folder
                return False
                
            # Try to create the directory or check if it's writable
            try:
                path.mkdir(parents=True, exist_ok=True)
                # Try to write a test file
                test_file = path / ".test_write"
                test_file.touch()
                test_file.unlink()
                self.folder_validation.config(text="")
                self.next_btn.config(state="normal") # Enable next on valid folder
                return True
            except (PermissionError, OSError):
                self.folder_validation.config(text="Cannot write to this location")
                self.next_btn.config(state="disabled") # Disable next on invalid folder
                return False
                
        except Exception as e:
            self.folder_validation.config(text=f"Invalid path: {str(e)}")
            self.next_btn.config(state="disabled") # Disable next on invalid folder
            return False
            
    def _test_camera(self):
        """Test the selected camera by taking a snapshot."""
        try:
            cap = cv2.VideoCapture(self.selected_camera.get())
            if not cap.isOpened():
                messagebox.showerror("Error", "Could not open camera")
                return
                
            ret, frame = cap.read()
            if ret:
                # Save test image
                test_path = Path(self.output_folder.get()) / "camera_test.jpg"
                cv2.imwrite(str(test_path), frame)
                messagebox.showinfo("Success", f"Camera test successful!\nTest image saved to:\n{test_path}")
            else:
                messagebox.showerror("Error", "Could not capture frame from camera")
                
            cap.release()
        except Exception as e:
            messagebox.showerror("Error", f"Camera test failed:\n{str(e)}")
            
    def _browse_folder(self):
        folder = filedialog.askdirectory(
            initialdir=self.output_folder.get(),
            title="Select Output Folder"
        )
        if folder:
            self.output_folder.set(folder)
            self._validate_folder()
            
    def _on_save(self):
        """Save the configuration and close the wizard."""
        # Final validation
        if not self._validate_folder():
            return
            
        # Save configuration
        self.result = {
            "camera_index": self.selected_camera.get(),
            "output_folder": str(Path(self.output_folder.get()))
        }
        
        self._cleanup()
        self.window.destroy()
        
    def _on_cancel(self):
        """Cancel the wizard."""
        self.result = None
        self._cleanup()
        self.window.destroy()
        
    def _cleanup(self):
        """Clean up resources."""
        self.preview_running = False
        if hasattr(self, 'preview_cap') and self.preview_cap is not None:
            self.preview_cap.release()
            self.preview_cap = None


class WebcamMonitor:
    """Tkinter GUI wrapper around OpenCV detection & recording logic."""

    def __init__(self, root):
        self.root = root
        self.root.title("Webcam Monitor – Motion & Human Detection")

        # Initialize all attributes that will be used
        self.running = False
        self.cap = None
        self.backSub = None
        self.face_cascade = None
        self.recording = False
        self.out = None
        self.frames_since_last_detection = 0
        self.frame_buffer = None
        self.frame_width = 0
        self.frame_height = 0
        self.fps = 30.0
        self.frame_delay = 1
        self.update_job = None
        self.settings_win = None
        self.master_recording = False
        self.master_out = None
        self.detections = []
        self.debug_mode = False
        self.is_fullscreen = False
        self.background_mode = False

        # Store parameter variables
        self.min_area_var = tk.IntVar(value=5000)
        self.pre_buffer_var = tk.IntVar(value=10)
        self.post_buffer_var = tk.IntVar(value=10)
        self.cam_index_var = tk.IntVar(value=0)
        self.always_record_var = tk.BooleanVar(value=True)
        
        # Create menu bar
        self._create_menu_bar()
        
        # Check if first run
        self.config_file = Path.home() / ".webcam_monitor_config.json"
        if not self.config_file.exists():
            self._run_first_time_wizard()
        else:
            self._load_config()

        # Default destination directory
        default_dir = Path.home() / "Videos" / "SecCam"
        default_dir.mkdir(parents=True, exist_ok=True)
        self.destination_dir = tk.StringVar(value=str(default_dir))

        # ==== Video panel ====
        self.video_label = ttk.Label(root)
        self.video_label.pack(padx=5, pady=5)

        self.status_var = tk.StringVar(value="Idle")
        ttk.Label(root, textvariable=self.status_var).pack(pady=(0, 5))

        # ==== Controls ====
        btn_frame = ttk.Frame(root)
        btn_frame.pack(pady=(0, 10))
        self.start_btn = ttk.Button(btn_frame, text="Start", command=self.start)
        self.start_btn.grid(row=0, column=0, padx=5)
        self.stop_btn = ttk.Button(btn_frame, text="Stop", command=self.stop, state="disabled")
        self.stop_btn.grid(row=0, column=1, padx=5)
        self.settings_btn = ttk.Button(btn_frame, text="Settings", command=self.toggle_settings)
        self.settings_btn.grid(row=0, column=2, padx=5)
        self.export_btn = ttk.Button(btn_frame, text="Export Log", command=self.export_log)
        self.export_btn.grid(row=0, column=3, padx=5)

        # ==== Detection list ====
        list_frame = ttk.Frame(root)
        list_frame.pack(fill="both", expand=True, padx=5, pady=(0, 10))
        ttk.Label(list_frame, text="Detections (double-click to open)").pack(anchor="w")

        self.detection_list = tk.Listbox(list_frame, height=8)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.detection_list.yview)
        self.detection_list.configure(yscrollcommand=scrollbar.set)
        self.detection_list.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.detection_list.bind("<Double-Button-1>", self.open_selected_clip)

        # Load face cascade classifier
        try:
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            if self.face_cascade.empty():
                messagebox.showwarning("Warning", "Failed to load face detection model.")
                self.face_cascade = None
        except Exception as e:
            messagebox.showwarning("Warning", f"Failed to load face detection model: {e}")
            self.face_cascade = None

        # Keyboard shortcut bindings
        self.root.bind("<space>", lambda e: self._toggle_recording())
        self.root.bind("<Escape>", lambda e: self._handle_escape())
        self.root.bind("<KeyPress-q>", lambda e: self.on_close())
        self.root.bind("<KeyPress-Q>", lambda e: self.on_close())
        self.root.bind("<KeyPress-d>", lambda e: self._toggle_debug())
        self.root.bind("<KeyPress-D>", lambda e: self._toggle_debug())
        self.root.bind("<Control-f>", lambda e: self._toggle_fullscreen())
        self.root.bind("<Control-F>", lambda e: self._toggle_fullscreen())
        self.root.bind("<Control-b>", lambda e: self._toggle_background())
        self.root.bind("<Control-B>", lambda e: self._toggle_background())
        self.root.bind_all("<KeyPress-s>", self.toggle_settings)
        self.root.bind_all("<KeyPress-S>", self.toggle_settings)

        # Close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _create_menu_bar(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Quick Start Wizard", command=self._run_first_time_wizard)
        file_menu.add_command(label="Settings", command=self.toggle_settings)
        file_menu.add_command(label="Export Log", command=self.export_log)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_close)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_checkbutton(label="Debug Mode", command=self._toggle_debug)
        view_menu.add_checkbutton(label="Fullscreen", command=self._toggle_fullscreen)
        view_menu.add_checkbutton(label="Background Mode", command=self._toggle_background)
        
        # Camera menu
        camera_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Camera", menu=camera_menu)
        camera_menu.add_command(label="Start", command=self.start)
        camera_menu.add_command(label="Stop", command=self.stop)
        camera_menu.add_separator()
        camera_menu.add_checkbutton(label="Always Record", variable=self.always_record_var)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Keyboard Shortcuts", command=self._show_shortcuts)
        help_menu.add_command(label="About", command=self._show_about)

    def _show_shortcuts(self):
        """Show keyboard shortcuts window."""
        shortcuts_win = tk.Toplevel(self.root)
        shortcuts_win.title("Keyboard Shortcuts")
        shortcuts_win.geometry("300x250")
        shortcuts_win.resizable(False, False)
        shortcuts_win.transient(self.root)
        
        # Center window
        shortcuts_win.update_idletasks()
        x = (shortcuts_win.winfo_screenwidth() // 2) - (shortcuts_win.winfo_width() // 2)
        y = (shortcuts_win.winfo_screenheight() // 2) - (shortcuts_win.winfo_height() // 2)
        shortcuts_win.geometry(f'+{x}+{y}')
        
        # Shortcuts text
        shortcuts_text = """
• Space - Start/Stop recording
• Esc - Close current window
• Q - Quit application
• D - Toggle debug overlay
• Ctrl + F - Toggle fullscreen
• Ctrl + B - Run in background
• S - Open settings
        """
        
        ttk.Label(shortcuts_win, text="Available Shortcuts", font=("", 12, "bold")).pack(pady=10)
        ttk.Label(shortcuts_win, text=shortcuts_text, justify="left").pack(padx=20)
        ttk.Button(shortcuts_win, text="Close", command=shortcuts_win.destroy).pack(pady=10)

    def _show_about(self):
        """Show about window."""
        about_win = tk.Toplevel(self.root)
        about_win.title("About Webcam Monitor")
        about_win.geometry("400x300")
        about_win.resizable(False, False)
        about_win.transient(self.root)
        
        # Center window
        about_win.update_idletasks()
        x = (about_win.winfo_screenwidth() // 2) - (about_win.winfo_width() // 2)
        y = (about_win.winfo_screenheight() // 2) - (about_win.winfo_height() // 2)
        about_win.geometry(f'+{x}+{y}')
        
        # About text
        about_text = """Webcam Monitor

Version 1.0

A desktop application for motion and human detection using your webcam. Features include:

• Motion detection
• Face detection
• Pre/post recording buffer
• Automatic clip saving
• Export capabilities
• Background operation mode

Created with Python, OpenCV, and Tkinter.

© 2025 All rights reserved."""
        
        ttk.Label(about_win, text="About", font=("", 14, "bold")).pack(pady=10)
        ttk.Label(about_win, text=about_text, wraplength=350, justify="center").pack(padx=20)
        ttk.Button(about_win, text="Close", command=about_win.destroy).pack(pady=10)

    def _toggle_recording(self):
        """Toggle recording state with space bar."""
        if self.running:
            self.stop()
        else:
            self.start()

    def _handle_escape(self):
        """Handle escape key press."""
        if self.is_fullscreen:
            self._toggle_fullscreen()
        elif self.settings_win is not None and self.settings_win.winfo_exists():
            self.settings_win.destroy()
            self.settings_win = None

    def _toggle_debug(self):
        """Toggle debug overlay mode."""
        self.debug_mode = not self.debug_mode
        self.status_var.set(f"Debug mode {'enabled' if self.debug_mode else 'disabled'}")

    def _toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes('-fullscreen', self.is_fullscreen)
        if self.is_fullscreen:
            # Hide all widgets except video
            for widget in self.root.winfo_children():
                if widget != self.video_label:
                    widget.pack_forget()
            self.video_label.pack(expand=True, fill="both")
        else:
            # Restore normal layout
            self.video_label.pack_forget()
            self.video_label.pack(padx=5, pady=5)
            # Restore other widgets
            for widget in self.root.winfo_children():
                if widget != self.video_label:
                    widget.pack()

    def _toggle_background(self):
        """Toggle background mode."""
        self.background_mode = not self.background_mode
        if self.background_mode:
            self.root.withdraw()  # Hide window
            self.status_var.set("Running in background")
        else:
            self.root.deiconify()  # Show window
            self.status_var.set("Running")

    def start(self):
        if self.running:
            return
            
        try:
            self.cap = cv2.VideoCapture(self.cam_index_var.get(), cv2.CAP_DSHOW)  # Try DirectShow backend first
            if not self.cap.isOpened():
                # If DirectShow fails, try the default backend
                self.cap = cv2.VideoCapture(self.cam_index_var.get())
                
            if not self.cap.isOpened():
                messagebox.showerror("Error", "Could not open webcam. Please check if it's connected and not in use by another application.")
                return

            # Frame properties for video writer
            self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps_from_cam = self.cap.get(cv2.CAP_PROP_FPS)
            self.fps = fps_from_cam if fps_from_cam > 0 else 30.0
            self.frame_delay = 1

            # Pre/Post buffer frame calculations
            self.pre_buffer_frames = int(self.pre_buffer_var.get() * self.fps)
            self.post_buffer_frames = int(self.post_buffer_var.get() * self.fps)
            self.frame_buffer = collections.deque(maxlen=self.pre_buffer_frames)

            # Background subtractor
            self.backSub = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50, detectShadows=True)

            self.running = True
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            self.status_var.set("Running")

            # Start frame loop
            self.update_frame()

            # Start master recording if option enabled
            if self.always_record_var.get() and not self.master_recording:
                self._start_master_recording()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start camera: {str(e)}")
            self._release_resources()

    # ------------------------------------------------------------------
    def stop(self):
        if not self.running:
            return
        self.running = False
        self.status_var.set("Stopping…")
        if self.update_job is not None:
            self.root.after_cancel(self.update_job)
            self.update_job = None
        self._release_resources()
        self.video_label.configure(image="")
        # Stop master recording if running
        self._stop_master_recording()
        self.status_var.set("Stopped")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

    # ------------------------------------------------------------------
    def update_frame(self):
        if not self.running:
            return
        ret, frame = self.cap.read()
        if not ret:
            self.status_var.set("Failed to grab frame")
            self.stop()
            return

        # Save raw frame to buffer (for pre-recording)
        raw_frame = frame.copy()
        if self.frame_buffer is not None:
            self.frame_buffer.append(raw_frame)

        # Main detection logic -------------------------------------------------
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Human detection
        human_detected = False
        if self.face_cascade is not None:
            for (x, y, w, h) in self.face_cascade.detectMultiScale(gray, 1.3, 5):
                human_detected = True
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                # Label the detected human
                label_y = y - 10 if y - 10 > 10 else y + h + 20
                cv2.putText(frame, "Human", (x, label_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        # Motion detection
        motion_detected = False
        if self.backSub is not None:
            fgMask = self.backSub.apply(frame)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            fgMask = cv2.morphologyEx(fgMask, cv2.MORPH_OPEN, kernel, iterations=2)
            contours, _ = cv2.findContours(fgMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                if cv2.contourArea(cnt) > self.min_area_var.get():
                    motion_detected = True
                    x, y, w, h = cv2.boundingRect(cnt)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if motion_detected or human_detected:
            cv2.putText(frame, "Motion/Human Detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            self.frames_since_last_detection = 0
            if not self.recording:
                filename_only = datetime.datetime.now().strftime("recording_%Y%m%d_%H%M%S.avi")
                filepath = os.path.join(self.destination_dir.get(), filename_only)
                # Ensure directory exists (user might have typed new path without browsing)
                Path(self.destination_dir.get()).mkdir(parents=True, exist_ok=True)
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                self.out = cv2.VideoWriter(filepath, fourcc, self.fps, (self.frame_width, self.frame_height))
                # Write pre-buffer frames first
                if self.frame_buffer is not None:
                    for bf in self.frame_buffer:
                        self.out.write(bf)
                self.recording = True
                # Log this detection
                timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.detections.append({"timestamp": timestamp_str, "filename": filepath})
                self.detection_list.insert(tk.END, f"{timestamp_str} – {filename_only}")
        else:
            if self.recording:
                self.frames_since_last_detection += 1
                if self.frames_since_last_detection > self.post_buffer_frames:
                    self._stop_recording()

        # Add debug overlay if enabled
        if self.debug_mode:
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, frame.shape[0] - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            cv2.putText(frame, f"Recording: {'Yes' if self.recording else 'No'}", 
                       (10, frame.shape[0] - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        if self.recording and self.out is not None:
            self.out.write(frame)

        # Convert and display in Tkinter
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Scale frame if in fullscreen mode
        if self.is_fullscreen:
            h, w = rgb.shape[:2]
            window_w = self.root.winfo_width()
            window_h = self.root.winfo_height()
            scale = min(window_w/w, window_h/h)
            new_w, new_h = int(w*scale), int(h*scale)
            rgb = cv2.resize(rgb, (new_w, new_h))
        
        img = ImageTk.PhotoImage(Image.fromarray(rgb))
        self.video_label.imgtk = img  # save reference
        self.video_label.configure(image=img)

        # Schedule next frame
        self.update_job = self.root.after(self.frame_delay, self.update_frame)

        # If master recording on, write raw frame
        if self.master_recording and self.master_out is not None:
            # Overlay current timestamp on the frame
            time_str = datetime.datetime.now().strftime("%H:%M:%S")
            overlay_frame = raw_frame.copy()
            cv2.putText(overlay_frame, time_str, (10, self.frame_height - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            self.master_out.write(overlay_frame)

    # ------------------------------------------------------------------
    def _stop_recording(self):
        if self.recording:
            self.recording = False
            if self.out is not None:
                self.out.release()
                self.out = None

    # ------------------------------------------------------------------
    def _release_resources(self):
        self._stop_recording()
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    # ------------------------------------------------------------------
    def on_close(self):
        self.stop()
        self.root.destroy()

    # ------------------------------------------------------------------
    def toggle_settings(self, event=None):
        # If window exists and is visible, close it (toggle behavior)
        if self.settings_win is not None and self.settings_win.winfo_exists():
            self.settings_win.destroy()
            self.settings_win = None
            return

        self.settings_win = tk.Toplevel(self.root)
        self.settings_win.title("Settings")
        self.settings_win.resizable(False, False)

        # When the window is closed via the window manager, clear reference
        self.settings_win.protocol("WM_DELETE_WINDOW", lambda: (self.settings_win.destroy(), setattr(self, 'settings_win', None)))

        row = 0
        ttk.Label(self.settings_win, text="Camera index:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        ttk.Spinbox(self.settings_win, from_=0, to=10, textvariable=self.cam_index_var, width=5).grid(row=row, column=1, padx=5, pady=5)

        row += 1
        ttk.Label(self.settings_win, text="Min motion area:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.settings_win, textvariable=self.min_area_var, width=10).grid(row=row, column=1, padx=5, pady=5)

        row += 1
        ttk.Label(self.settings_win, text="Pre-record buffer (s):").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.settings_win, textvariable=self.pre_buffer_var, width=10).grid(row=row, column=1, padx=5, pady=5)

        row += 1
        ttk.Label(self.settings_win, text="Post-record buffer (s):").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.settings_win, textvariable=self.post_buffer_var, width=10).grid(row=row, column=1, padx=5, pady=5)

        # Always record checkbox
        row += 1
        ttk.Checkbutton(self.settings_win, text="Always record (master clip)", variable=self.always_record_var).grid(row=row, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        # Destination directory row
        row += 1
        ttk.Label(self.settings_win, text="Save directory:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        dir_entry = ttk.Entry(self.settings_win, textvariable=self.destination_dir, width=30)
        dir_entry.grid(row=row, column=1, padx=5, pady=5)
        ttk.Button(self.settings_win, text="Browse…", command=self._browse_destination).grid(row=row, column=2, padx=5, pady=5)

        row += 1
        ttk.Button(self.settings_win, text="Close", command=self.settings_win.destroy).grid(row=row, column=0, columnspan=3, pady=10)

    # ------------------------------------------------------------------
    def open_selected_clip(self, event=None):
        selection = self.detection_list.curselection()
        if not selection:
            return
        idx = selection[0]
        clip_path = self.detections[idx]["filename"]
        try:
            if platform.system() == "Windows":
                os.startfile(clip_path)
            elif platform.system() == "Darwin":
                import subprocess
                subprocess.Popen(["open", clip_path])
            else:
                import subprocess
                subprocess.Popen(["xdg-open", clip_path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open clip:\n{e}")

    # ------------------------------------------------------------------
    def export_log(self):
        if not self.detections:
            messagebox.showinfo("Export Log", "No detections to export yet.")
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not filepath:
            return  # user cancelled
        try:
            import csv
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Filename"])
                for det in self.detections:
                    writer.writerow([det["timestamp"], det["filename"]])
            messagebox.showinfo("Export Log", f"Log exported to {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export log:\n{e}")

    # ------------------------------------------------------------------
    def _browse_destination(self):
        selected = filedialog.askdirectory(initialdir=self.destination_dir.get() or str(Path.home()), title="Select destination folder")
        if selected:
            self.destination_dir.set(selected)
            # Ensure directory exists
            Path(selected).mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    def _start_master_recording(self):
        if self.master_recording:
            return
        filename_only = datetime.datetime.now().strftime("master_%Y%m%d_%H%M%S.avi")
        filepath = os.path.join(self.destination_dir.get(), filename_only)
        Path(self.destination_dir.get()).mkdir(parents=True, exist_ok=True)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.master_out = cv2.VideoWriter(filepath, fourcc, self.fps, (self.frame_width, self.frame_height))
        if self.master_out.isOpened():
            self.master_recording = True

    # ------------------------------------------------------------------
    def _stop_master_recording(self):
        if self.master_recording:
            self.master_recording = False
            if self.master_out is not None:
                self.master_out.release()
                self.master_out = None

    def _run_first_time_wizard(self):
        wizard = FirstRunWizard(self.root)
        self.root.wait_window(wizard.window)
        if wizard.result:
            self._save_config(wizard.result)
            self._load_config() # Reload config to apply new settings
            messagebox.showinfo("Setup Complete", "Webcam Monitor has been configured for your first run.")
        else:
            messagebox.showwarning("Setup Cancelled", "Webcam Monitor setup was cancelled.")

    def _save_config(self, config):
        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration:\n{e}")

    def _load_config(self):
        try:
            with open(self.config_file, "r") as f:
                config = json.load(f)
                self.cam_index_var.set(config["camera_index"])
                self.destination_dir.set(config["output_folder"])
                # Ensure the directory exists after loading
                Path(self.destination_dir.get()).mkdir(parents=True, exist_ok=True)
        except FileNotFoundError:
            # If config file not found, use default values
            self.cam_index_var.set(0)
            self.destination_dir.set(str(Path.home() / "Videos" / "SecCam"))
            Path(self.destination_dir.get()).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration:\n{e}")


# ============================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = WebcamMonitor(root)
    root.mainloop() 