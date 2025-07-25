"""Main window module."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import webbrowser
import platform
import subprocess
from pathlib import Path
import datetime
import csv

from ..core.camera import Camera
from ..core.detection import Detector
from ..core.recording import VideoRecorder
from ..utils.config import Config
from ..utils.video import frame_to_tkimage, resize_frame
from .wizard import SetupWizard
from .settings import SettingsDialog
from ..utils.app_info import (
    APP_NAME, APP_VERSION, APP_DESCRIPTION,
    COMPANY_NAME, COPYRIGHT_TEXT,
    DEV_NAME, DEV_LINK,
    TITLE_FONT, SUBTITLE_FONT, BODY_FONT, LINK_FONT, LINK_COLOR,
    ABOUT_WINDOW_SIZE, ABOUT_WINDOW_PADDING,
    DESCRIPTION_WRAP_LENGTH
)

class MainWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Webcam Monitor – Motion & Human Detection")
        
        # Initialize components
        self.config = Config()
        self.camera: Optional[Camera] = None
        self.detector: Optional[Detector] = None
        self.recorder: Optional[VideoRecorder] = None
        
        # State variables
        self.running = False
        self.update_job: Optional[str] = None
        
        # Create GUI
        self._create_menu()
        self._create_widgets()
        
        # Bind keyboard shortcuts
        self._bind_shortcuts()
        
        # Check first run
        if not self.config.config_file.exists():
            self._run_first_time_wizard()
            
        # Close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _create_menu(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Quick Start Wizard",
                            command=self._run_first_time_wizard)
        file_menu.add_command(label="Settings",
                            command=self._show_settings)
        file_menu.add_command(label="Export Log",
                            command=self._export_log)
        file_menu.add_separator()
        file_menu.add_command(label="Exit",
                            command=self.on_close)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_checkbutton(label="Debug Mode",
                                variable=self.config.debug_mode)
        view_menu.add_checkbutton(label="Fullscreen",
                                command=self._toggle_fullscreen)
        view_menu.add_checkbutton(label="Background Mode",
                                command=self._toggle_background)
        
        # Camera menu
        camera_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Camera", menu=camera_menu)
        camera_menu.add_command(label="Start",
                              command=self.start)
        camera_menu.add_command(label="Stop",
                              command=self.stop)
        camera_menu.add_separator()
        camera_menu.add_checkbutton(label="Always Record",
                                  variable=self.config.always_record)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Keyboard Shortcuts",
                            command=self._show_shortcuts)
        help_menu.add_command(label="About",
                            command=self._show_about)

    def _create_widgets(self):
        """Create the main window widgets."""
        # Video panel
        self.video_label = ttk.Label(self.root)
        self.video_label.pack(padx=5, pady=5)
        
        # Status
        self.status_var = tk.StringVar(value="Idle")
        ttk.Label(self.root, textvariable=self.status_var).pack(pady=(0, 5))
        
        # Controls
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=(0, 10))
        
        self.start_btn = ttk.Button(btn_frame, text="Start",
                                  command=self.start)
        self.start_btn.grid(row=0, column=0, padx=5)
        
        self.stop_btn = ttk.Button(btn_frame, text="Stop",
                                 command=self.stop,
                                 state="disabled")
        self.stop_btn.grid(row=0, column=1, padx=5)
        
        self.settings_btn = ttk.Button(btn_frame, text="Settings",
                                    command=self._show_settings)
        self.settings_btn.grid(row=0, column=2, padx=5)
        
        self.export_btn = ttk.Button(btn_frame, text="Export Log",
                                   command=self._export_log)
        self.export_btn.grid(row=0, column=3, padx=5)
        
        # Detection list
        list_frame = ttk.Frame(self.root)
        list_frame.pack(fill="both", expand=True, padx=5, pady=(0, 10))
        ttk.Label(list_frame, text="Detections (double-click to open)").pack(anchor="w")
        
        self.detection_list = tk.Listbox(list_frame, height=8)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical",
                                command=self.detection_list.yview)
        self.detection_list.configure(yscrollcommand=scrollbar.set)
        self.detection_list.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.detection_list.bind("<Double-Button-1>", self._open_selected_clip)
        
        # Detection storage
        self.detections: List[Dict[str, str]] = []

    def _bind_shortcuts(self):
        """Bind keyboard shortcuts."""
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
        self.root.bind("<KeyPress-s>", lambda e: self._show_settings())
        self.root.bind("<KeyPress-S>", lambda e: self._show_settings())

    def start(self):
        """Start video capture and processing."""
        if self.running:
            return
            
        # Initialize camera
        self.camera = Camera(self.config.camera_index)
        if not self.camera.open():
            messagebox.showerror(
                "Error",
                "Could not open webcam. Please check if it's connected and not in use."
            )
            return
            
        # Initialize detector
        self.detector = Detector(self.config.min_motion_area)
        
        # Initialize recorder
        self.recorder = VideoRecorder(
            self.config.output_folder,
            self.camera.frame_width,
            self.camera.frame_height,
            self.camera.fps,
            self.config.pre_buffer_seconds,
            self.config.post_buffer_seconds
        )
        
        # Start master recording if enabled
        if self.config.always_record:
            self.recorder.start_master_recording()
        
        self.running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.status_var.set("Running")
        
        # Start frame processing
        self._process_frame()

    def stop(self):
        """Stop video capture and processing."""
        if not self.running:
            return
            
        self.running = False
        if self.update_job is not None:
            self.root.after_cancel(self.update_job)
            self.update_job = None
            
        # Release resources
        if self.camera:
            self.camera.release()
            self.camera = None
            
        if self.recorder:
            self.recorder.release()
            self.recorder = None
            
        self.detector = None
        
        # Update UI
        self.video_label.configure(image="")
        self.status_var.set("Stopped")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

    def _process_frame(self):
        """Process a single frame."""
        if not self.running or not self.camera or not self.detector or not self.recorder:
            return
            
        # Read frame
        ret, frame = self.camera.read_frame()
        if not ret:
            self.status_var.set("Failed to grab frame")
            self.stop()
            return
            
        # Process frame
        processed_frame, motion_detected, faces_detected = self.detector.process_frame(
            frame,
            self.config.debug_mode
        )
        
        # Handle recording
        was_recording = self.recorder.is_recording
        self.recorder.add_frame(
            processed_frame,
            motion_detected or faces_detected,
            timestamp=True
        )
        
        # Log new detections
        if not was_recording and self.recorder.is_recording:
            # A new recording has started
            timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            filename = self.recorder.current_recording_file
            if filename:  # Make sure we have a valid filename
                self.detections.append({
                    "timestamp": timestamp_str,
                    "filename": filename
                })
                self.detection_list.insert(tk.END, f"{timestamp_str} – {Path(filename).name}")
                # Auto-scroll to the latest detection
                self.detection_list.see(tk.END)
        
        # Convert for display
        if self.config.fullscreen:
            # Scale to window size
            window_width = self.root.winfo_width()
            window_height = self.root.winfo_height()
            processed_frame = resize_frame(
                processed_frame,
                width=window_width,
                height=window_height
            )
            
        display_image = frame_to_tkimage(processed_frame)
        self.video_label.imgtk = display_image
        self.video_label.configure(image=display_image)
        
        # Schedule next frame
        self.update_job = self.root.after(1, self._process_frame)

    def _run_first_time_wizard(self):
        """Run the first-time setup wizard."""
        wizard = SetupWizard(self.root)
        self.root.wait_window(wizard.window)
        
        if wizard.result:
            self.config.update(wizard.result)
            self.config.save()
            messagebox.showinfo(
                "Setup Complete",
                "Webcam Monitor has been configured for your first run."
            )
        else:
            messagebox.showwarning(
                "Setup Cancelled",
                "Webcam Monitor setup was cancelled."
            )

    def _show_settings(self):
        """Show the settings dialog."""
        dialog = SettingsDialog(self.root, self.config)
        self.root.wait_window(dialog.window)

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
        
        ttk.Label(shortcuts_win, text="Available Shortcuts",
                 font=("", 12, "bold")).pack(pady=10)
        ttk.Label(shortcuts_win, text=shortcuts_text,
                 justify="left").pack(padx=20)
        ttk.Button(shortcuts_win, text="Close",
                  command=shortcuts_win.destroy).pack(pady=10)

    def _show_about(self):
        """Show about window."""
        about_win = tk.Toplevel(self.root)
        about_win.title(f"About {APP_NAME}")
        about_win.geometry(ABOUT_WINDOW_SIZE)
        about_win.resizable(False, False)
        about_win.transient(self.root)
        
        # Center window
        about_win.update_idletasks()
        x = (about_win.winfo_screenwidth() // 2) - (about_win.winfo_width() // 2)
        y = (about_win.winfo_screenheight() // 2) - (about_win.winfo_height() // 2)
        about_win.geometry(f'+{x}+{y}')
        
        # Create a frame with padding
        main_frame = ttk.Frame(about_win, padding=ABOUT_WINDOW_PADDING)
        main_frame.pack(fill="both", expand=True)
        
        # App title and version
        ttk.Label(main_frame, text=APP_NAME, 
                 font=TITLE_FONT).pack(pady=(0, 5))
        ttk.Label(main_frame, text=f"Version: {APP_VERSION}", 
                 font=SUBTITLE_FONT).pack(pady=(0, 20))
        
        # Description
        ttk.Label(main_frame, text=APP_DESCRIPTION, 
                 justify="left", wraplength=DESCRIPTION_WRAP_LENGTH).pack(pady=(0, 20))
        
        # Credits
        credits_frame = ttk.Frame(main_frame)
        credits_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(credits_frame, text=f"Created by {COMPANY_NAME}",
                 font=BODY_FONT).pack()
        
        # Developer info with clickable link
        dev_frame = ttk.Frame(credits_frame)
        dev_frame.pack(pady=5)
        ttk.Label(dev_frame, text="Developed by ", font=BODY_FONT).pack(side="left")
        dev_label = ttk.Label(dev_frame, text=DEV_NAME,
                            font=LINK_FONT, foreground=LINK_COLOR,
                            cursor="hand2")
        dev_label.pack(side="left")
        
        def _handle_dev_click(event):
            """Handle click on developer name: copy link and open browser."""
            # Copy to clipboard
            self.root.clipboard_clear()
            self.root.clipboard_append(DEV_LINK)
            self.root.update()  # Required for Linux
            
            # Show tooltip
            tooltip = tk.Toplevel(about_win)
            tooltip.overrideredirect(True)
            tooltip.attributes('-topmost', True)
            
            # Position tooltip near mouse
            tooltip.geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            # Add message
            ttk.Label(tooltip, text="Link copied to clipboard!", 
                     padding=5).pack()
            
            # Open in browser
            webbrowser.open(DEV_LINK)
            
            # Destroy tooltip after 2 seconds
            about_win.after(2000, tooltip.destroy)
        
        dev_label.bind("<Button-1>", _handle_dev_click)
        
        ttk.Label(credits_frame, text=COPYRIGHT_TEXT,
                 font=BODY_FONT).pack()
        
        # Close button
        ttk.Button(main_frame, text="Close",
                  command=about_win.destroy).pack(pady=(20, 0))

    def _open_website(self, url: str):
        """Open website in default browser."""
        import webbrowser
        webbrowser.open(url)

    def _export_log(self):
        """Export detection log to CSV."""
        if not self.detections:
            messagebox.showinfo("Export Log", "No detections to export yet.")
            return
            
        filepath = tk.filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
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

    def _open_selected_clip(self, event=None):
        """Open the selected clip in the system's default video player."""
        selection = self.detection_list.curselection()
        if not selection:
            return
            
        idx = selection[0]
        clip_path = self.detections[idx]["filename"]
        
        try:
            import os
            import platform
            import subprocess
            
            if platform.system() == "Windows":
                os.startfile(clip_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", clip_path])
            else:  # Linux
                subprocess.Popen(["xdg-open", clip_path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open clip:\n{e}")

    def _toggle_recording(self):
        """Toggle recording state."""
        if self.running:
            self.stop()
        else:
            self.start()

    def _toggle_debug(self):
        """Toggle debug overlay."""
        self.config.debug_mode = not self.config.debug_mode
        self.status_var.set(
            f"Debug mode {'enabled' if self.config.debug_mode else 'disabled'}"
        )

    def _toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        self.config.fullscreen = not self.config.fullscreen
        self.root.attributes('-fullscreen', self.config.fullscreen)
        
        if self.config.fullscreen:
            # Hide all widgets except video
            for widget in self.root.winfo_children():
                if widget != self.video_label:
                    widget.pack_forget()
            self.video_label.pack(expand=True, fill="both")
        else:
            # Restore normal layout
            self._create_widgets()

    def _toggle_background(self):
        """Toggle background mode."""
        self.config.background_mode = not self.config.background_mode
        if self.config.background_mode:
            self.root.withdraw()  # Hide window
            self.status_var.set("Running in background")
        else:
            self.root.deiconify()  # Show window
            self.status_var.set("Running")

    def _handle_escape(self):
        """Handle escape key press."""
        if self.config.fullscreen:
            self._toggle_fullscreen()

    def on_close(self):
        """Handle application close."""
        self.stop()
        self.config.save()
        self.root.destroy() 