"""Camera handling module for webcam access and frame capture."""

import cv2
import numpy as np
from typing import Optional, Tuple, List

class Camera:
    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index
        self.cap = None
        self.frame_width = 0
        self.frame_height = 0
        self.fps = 30.0

    def open(self) -> bool:
        """Open the camera with DirectShow backend first, fallback to default."""
        try:
            # Try DirectShow backend first (better for Windows)
            self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                # Fallback to default backend
                self.cap = cv2.VideoCapture(self.camera_index)
                
            if not self.cap.isOpened():
                return False

            # Get camera properties
            self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps_from_cam = self.cap.get(cv2.CAP_PROP_FPS)
            self.fps = fps_from_cam if fps_from_cam > 0 else 30.0
            
            return True
        except Exception:
            return False

    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Read a frame from the camera."""
        if not self.cap or not self.cap.isOpened():
            return False, None
        return self.cap.read()

    def release(self):
        """Release the camera resources."""
        if self.cap:
            self.cap.release()
            self.cap = None

    @staticmethod
    def list_cameras(max_cameras: int = 5) -> List[int]:
        """List available cameras."""
        available_cameras = []
        for i in range(max_cameras):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    available_cameras.append(i)
                cap.release()
        return available_cameras

    def get_properties(self) -> dict:
        """Get camera properties."""
        return {
            'frame_width': self.frame_width,
            'frame_height': self.frame_height,
            'fps': self.fps,
            'backend': 'DirectShow' if self.cap and self.cap.get(cv2.CAP_PROP_BACKEND) == cv2.CAP_DSHOW else 'Default'
        }

    def is_opened(self) -> bool:
        """Check if camera is opened."""
        return self.cap is not None and self.cap.isOpened() 