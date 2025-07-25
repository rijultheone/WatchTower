"""Detection module for motion and face detection."""

import cv2
import numpy as np
from typing import List, Tuple, Optional

class Detector:
    def __init__(self, min_motion_area: int = 5000):
        self.min_motion_area = min_motion_area
        self.backSub = cv2.createBackgroundSubtractorMOG2(
            history=500,
            varThreshold=50,
            detectShadows=True
        )
        
        # Load face detection model
        try:
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            if self.face_cascade.empty():
                self.face_cascade = None
        except Exception:
            self.face_cascade = None

    def detect_motion(self, frame: np.ndarray) -> Tuple[bool, List[Tuple[int, int, int, int]]]:
        """
        Detect motion in frame.
        Returns: (motion_detected, list of motion regions as (x, y, w, h))
        """
        motion_regions = []
        
        # Apply background subtraction
        fgMask = self.backSub.apply(frame)
        
        # Clean up the mask
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        fgMask = cv2.morphologyEx(fgMask, cv2.MORPH_OPEN, kernel, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(
            fgMask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Process contours
        motion_detected = False
        for cnt in contours:
            if cv2.contourArea(cnt) > self.min_motion_area:
                motion_detected = True
                x, y, w, h = cv2.boundingRect(cnt)
                motion_regions.append((x, y, w, h))
                
        return motion_detected, motion_regions

    def detect_faces(self, frame: np.ndarray) -> Tuple[bool, List[Tuple[int, int, int, int]]]:
        """
        Detect faces in frame.
        Returns: (faces_detected, list of face regions as (x, y, w, h))
        """
        if self.face_cascade is None:
            return False, []
            
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.3,
            minNeighbors=5
        )
        
        return len(faces) > 0, list(faces)

    def process_frame(self, frame: np.ndarray, debug: bool = False) -> Tuple[np.ndarray, bool, bool]:
        """
        Process a frame for both motion and face detection.
        Returns: (processed_frame, motion_detected, faces_detected)
        """
        frame_out = frame.copy()
        
        # Detect motion
        motion_detected, motion_regions = self.detect_motion(frame)
        
        # Detect faces
        faces_detected, face_regions = self.detect_faces(frame)
        
        # Draw motion regions
        for x, y, w, h in motion_regions:
            cv2.rectangle(frame_out, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
        # Draw face regions
        for x, y, w, h in face_regions:
            cv2.rectangle(frame_out, (x, y), (x + w, y + h), (255, 0, 0), 2)
            # Label the face
            label_y = y - 10 if y - 10 > 10 else y + h + 20
            cv2.putText(frame_out, "Human", (x, label_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            
        # Add detection status
        if motion_detected or faces_detected:
            cv2.putText(frame_out, "Motion/Human Detected",
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
        # Add debug info if requested
        if debug:
            height = frame_out.shape[0]
            cv2.putText(frame_out, f"Motion: {motion_detected}",
                       (10, height - 50), cv2.FONT_HERSHEY_SIMPLEX,
                       0.6, (255, 255, 0), 2)
            cv2.putText(frame_out, f"Faces: {faces_detected}",
                       (10, height - 30), cv2.FONT_HERSHEY_SIMPLEX,
                       0.6, (255, 255, 0), 2)
            
        return frame_out, motion_detected, faces_detected 