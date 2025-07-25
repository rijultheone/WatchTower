"""First-time setup wizard module."""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import cv2
from typing import Optional, Dict, Any

from ..core.camera import Camera
from ..utils.video import frame_to_tkimage

class SetupWizard:
    def __init__(self, parent: tk.Tk):
        self.window = tk.Toplevel(parent)
        self.window.title("Setup Wizard")
        self.window.geometry("500x400")
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
        
        # Camera preview state
        self.preview_running = False
        self.preview_cap: Optional[Camera] = None
        
        # Result storage
        self.result: Optional[Dict[str, Any]] = None
        
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
        """Create the welcome page."""
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
        """Create the camera setup page."""
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
        """Create the storage setup page."""
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
        """Create the hotkeys information page."""
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
        
    def show_step(self, step: int):
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
            self._stop_camera_preview()
        
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
        available_cameras = Camera.list_cameras()
        
        if not available_cameras:
            cameras = ["No cameras found"]
            messagebox.showwarning(
                "No Cameras",
                "No working cameras were detected.\nPlease connect a camera and click Refresh."
            )
        else:
            cameras = [f"Camera {i}" for i in available_cameras]
        
        self.camera_combo['values'] = cameras
        if cameras[0] != "No cameras found":
            self.camera_combo.current(0)
            self.selected_camera.set(available_cameras[0])
            
    def _start_camera_preview(self):
        """Start the camera preview."""
        self.preview_running = True
        self.preview_cap = None
        self._update_preview()
        
    def _stop_camera_preview(self):
        """Stop the camera preview."""
        self.preview_running = False
        if self.preview_cap is not None:
            self.preview_cap.release()
            self.preview_cap = None
        
    def _update_preview(self):
        """Update the camera preview frame."""
        if not self.preview_running:
            return
            
        if self.camera_combo.get().startswith("No cameras"):
            self._stop_camera_preview()
            self.preview_label.configure(image="")
            self.window.after(1000, self._update_preview)
            return
            
        try:
            if self.preview_cap is None:
                self.preview_cap = Camera(self.selected_camera.get())
                if not self.preview_cap.open():
                    raise RuntimeError("Failed to open camera")
            
            ret, frame = self.preview_cap.read_frame()
            if ret:
                # Resize frame to fit in the window
                frame = cv2.resize(frame, (320, 240))
                # Convert to PhotoImage
                img = frame_to_tkimage(frame)
                self.preview_label.imgtk = img
                self.preview_label.configure(image=img)
            
        except Exception as e:
            print(f"Preview error: {e}")
            
        self.window.after(33, self._update_preview)  # ~30 fps
            
    def _test_camera(self):
        """Test the selected camera by taking a snapshot."""
        try:
            camera = Camera(self.selected_camera.get())
            if not camera.open():
                messagebox.showerror("Error", "Could not open camera")
                return
                
            ret, frame = camera.read_frame()
            camera.release()
            
            if ret:
                # Save test image
                test_path = Path(self.output_folder.get()) / "camera_test.jpg"
                cv2.imwrite(str(test_path), frame)
                messagebox.showinfo(
                    "Success",
                    f"Camera test successful!\nTest image saved to:\n{test_path}"
                )
            else:
                messagebox.showerror("Error", "Could not capture frame from camera")
                
        except Exception as e:
            messagebox.showerror("Error", f"Camera test failed:\n{str(e)}")
            
    def _browse_folder(self):
        """Browse for output folder."""
        folder = tk.filedialog.askdirectory(
            initialdir=self.output_folder.get(),
            title="Select Output Folder"
        )
        if folder:
            self.output_folder.set(folder)
            self._validate_folder()
            
    def _validate_folder(self) -> bool:
        """Validate the output folder path."""
        folder = self.output_folder.get()
        try:
            path = Path(folder)
            # Check if path is absolute
            if not path.is_absolute():
                self.folder_validation.config(text="Please enter an absolute path")
                self.next_btn.config(state="disabled")
                return False
                
            # Check if parent directory exists and is writable
            parent = path.parent
            if not parent.exists():
                self.folder_validation.config(text="Parent directory does not exist")
                self.next_btn.config(state="disabled")
                return False
                
            # Try to create the directory or check if it's writable
            try:
                path.mkdir(parents=True, exist_ok=True)
                # Try to write a test file
                test_file = path / ".test_write"
                test_file.touch()
                test_file.unlink()
                self.folder_validation.config(text="")
                self.next_btn.config(state="normal")
                return True
            except (PermissionError, OSError):
                self.folder_validation.config(text="Cannot write to this location")
                self.next_btn.config(state="disabled")
                return False
                
        except Exception as e:
            self.folder_validation.config(text=f"Invalid path: {str(e)}")
            self.next_btn.config(state="disabled")
            return False
            
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
        self._stop_camera_preview() 