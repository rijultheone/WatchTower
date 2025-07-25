"""Core package for Webcam Monitor."""

from .camera import Camera
from .detection import Detector
from .recording import VideoRecorder

__all__ = ['Camera', 'Detector', 'VideoRecorder'] 