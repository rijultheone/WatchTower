"""Video utility module for frame processing and conversion."""

import cv2
import numpy as np
from PIL import Image, ImageTk
from typing import Tuple, Optional

def resize_frame(frame: np.ndarray, width: Optional[int] = None,
                height: Optional[int] = None) -> np.ndarray:
    """
    Resize frame maintaining aspect ratio.
    If both width and height are provided, fit within those dimensions.
    """
    if width is None and height is None:
        return frame
        
    h, w = frame.shape[:2]
    if width is None:
        # Scale based on height
        scale = height / h
        new_width = int(w * scale)
        new_height = height
    elif height is None:
        # Scale based on width
        scale = width / w
        new_width = width
        new_height = int(h * scale)
    else:
        # Fit within both dimensions
        scale = min(width/w, height/h)
        new_width = int(w * scale)
        new_height = int(h * scale)
        
    return cv2.resize(frame, (new_width, new_height))

def frame_to_tkimage(frame: np.ndarray) -> ImageTk.PhotoImage:
    """Convert OpenCV frame to Tkinter PhotoImage."""
    # Convert BGR to RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # Convert to PIL Image
    image = Image.fromarray(rgb)
    # Convert to PhotoImage
    return ImageTk.PhotoImage(image=image)

def add_timestamp(frame: np.ndarray, timestamp: str,
                 position: Tuple[int, int] = None,
                 color: Tuple[int, int, int] = (0, 255, 255),
                 size: float = 0.7,
                 thickness: int = 2) -> np.ndarray:
    """Add timestamp to frame."""
    frame = frame.copy()
    
    if position is None:
        # Default to bottom-left
        position = (10, frame.shape[0] - 10)
        
    cv2.putText(frame, timestamp, position,
                cv2.FONT_HERSHEY_SIMPLEX, size, color, thickness)
    return frame

def add_text_overlay(frame: np.ndarray, text: str,
                    position: Tuple[int, int],
                    color: Tuple[int, int, int] = (255, 255, 255),
                    size: float = 0.6,
                    thickness: int = 2,
                    background: bool = False) -> np.ndarray:
    """Add text overlay to frame with optional background."""
    frame = frame.copy()
    
    # Get text size
    (text_width, text_height), baseline = cv2.getTextSize(
        text, cv2.FONT_HERSHEY_SIMPLEX, size, thickness)
    
    if background:
        # Add dark background rectangle
        x, y = position
        cv2.rectangle(frame,
                     (x, y - text_height - baseline),
                     (x + text_width, y + baseline),
                     (0, 0, 0), cv2.FILLED)
    
    # Add text
    cv2.putText(frame, text, position,
                cv2.FONT_HERSHEY_SIMPLEX, size, color, thickness)
    
    return frame

def draw_detection_box(frame: np.ndarray,
                      box: Tuple[int, int, int, int],
                      label: Optional[str] = None,
                      color: Tuple[int, int, int] = (0, 255, 0),
                      thickness: int = 2) -> np.ndarray:
    """Draw detection box with optional label."""
    frame = frame.copy()
    x, y, w, h = box
    
    # Draw box
    cv2.rectangle(frame, (x, y), (x + w, y + h), color, thickness)
    
    # Add label if provided
    if label:
        # Determine label position (above box if possible)
        label_y = y - 10 if y - 10 > 10 else y + h + 20
        cv2.putText(frame, label, (x, label_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, thickness)
    
    return frame 