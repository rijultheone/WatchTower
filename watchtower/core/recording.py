"""Recording module for video capture and saving."""

import cv2
import datetime
from pathlib import Path
from collections import deque
import numpy as np
from typing import Optional, Deque

class VideoRecorder:
    def __init__(self, output_dir: str, frame_width: int, frame_height: int,
                 fps: float, pre_buffer_seconds: int = 10,
                 post_buffer_seconds: int = 10):
        self.output_dir = Path(output_dir)
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.fps = fps
        
        # Calculate buffer sizes
        self.pre_buffer_frames = int(pre_buffer_seconds * fps)
        self.post_buffer_frames = int(post_buffer_seconds * fps)
        
        # Initialize buffers and state
        self.frame_buffer: Deque[np.ndarray] = deque(maxlen=self.pre_buffer_frames)
        self.frames_since_last_detection = 0
        self.recording = False
        self.writer = None
        self.current_recording_file: Optional[str] = None
        
        # Master recording (continuous)
        self.master_recording = False
        self.master_writer = None
        self.current_master_file: Optional[str] = None
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def add_frame(self, frame: np.ndarray, detection: bool = False,
                 timestamp: bool = True) -> None:
        """Add a frame to the buffer and handle recording state."""
        # Store raw frame in buffer
        self.frame_buffer.append(frame.copy())
        
        if detection and not self.recording:
            self._start_recording()
        elif self.recording and not detection:
            self.frames_since_last_detection += 1
            if self.frames_since_last_detection > self.post_buffer_frames:
                self._stop_recording()
                
        # Write frame if recording
        if self.recording and self.writer is not None:
            self.writer.write(frame)
            
        # Handle master recording
        if self.master_recording and self.master_writer is not None:
            if timestamp:
                frame_with_time = frame.copy()
                time_str = datetime.datetime.now().strftime("%H:%M:%S")
                cv2.putText(frame_with_time, time_str,
                          (10, self.frame_height - 10),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                self.master_writer.write(frame_with_time)
            else:
                self.master_writer.write(frame)

    def _start_recording(self) -> None:
        """Start a new recording."""
        if self.recording:
            return
            
        # Generate filename with timestamp
        filename = datetime.datetime.now().strftime("recording_%Y%m%d_%H%M%S.avi")
        filepath = self.output_dir / filename
        self.current_recording_file = str(filepath)
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.writer = cv2.VideoWriter(
            self.current_recording_file,
            fourcc,
            self.fps,
            (self.frame_width, self.frame_height)
        )
        
        # Write pre-buffer frames
        for frame in self.frame_buffer:
            self.writer.write(frame)
            
        self.recording = True
        self.frames_since_last_detection = 0

    def _stop_recording(self) -> None:
        """Stop the current recording."""
        if not self.recording:
            return
            
        self.recording = False
        if self.writer is not None:
            self.writer.release()
            self.writer = None
        self.current_recording_file = None
        self.frames_since_last_detection = 0

    def start_master_recording(self) -> None:
        """Start continuous master recording."""
        if self.master_recording:
            return
            
        # Generate filename with timestamp
        filename = datetime.datetime.now().strftime("master_%Y%m%d_%H%M%S.avi")
        filepath = self.output_dir / filename
        self.current_master_file = str(filepath)
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.master_writer = cv2.VideoWriter(
            self.current_master_file,
            fourcc,
            self.fps,
            (self.frame_width, self.frame_height)
        )
        
        self.master_recording = True

    def stop_master_recording(self) -> None:
        """Stop master recording."""
        if not self.master_recording:
            return
            
        self.master_recording = False
        if self.master_writer is not None:
            self.master_writer.release()
            self.master_writer = None
        self.current_master_file = None

    def release(self) -> None:
        """Release all resources."""
        self._stop_recording()
        self.stop_master_recording()
        self.frame_buffer.clear()

    @property
    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self.recording

    @property
    def is_master_recording(self) -> bool:
        """Check if master recording is active."""
        return self.master_recording 