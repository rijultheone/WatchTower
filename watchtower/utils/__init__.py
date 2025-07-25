"""Utility package for Webcam Monitor."""

from .config import Config
from .video import (
    resize_frame,
    frame_to_tkimage,
    add_timestamp,
    add_text_overlay,
    draw_detection_box
)

__all__ = [
    'Config',
    'resize_frame',
    'frame_to_tkimage',
    'add_timestamp',
    'add_text_overlay',
    'draw_detection_box'
] 