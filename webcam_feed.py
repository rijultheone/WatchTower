import cv2
import numpy as np
import datetime

def main():
    # 0 is usually the built-in webcam. Use 1, 2, … for external cameras.
    cap = cv2.VideoCapture(0)

    # Initialize background subtractor for motion detection
    backSub = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50, detectShadows=True)
    # Load Haar cascade for human (face) detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    min_motion_area = 5000  # Minimum contour area to be considered motion

    # Video recording parameters
    recording = False
    frames_since_last_detection = 0
    BUFFER_AFTER_DETECTION = 60  # frames (~2 sec @30fps) to keep recording after activity stops
    out = None

    # Obtain frame properties for the video writer
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0  # fallback to 30 if camera doesn't report fps

    if not cap.isOpened():
        raise RuntimeError("Could not open webcam. Make sure it is not in use by another app.")

    print("Press  q  to quit the video window.")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame.")
                break

            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Human detection (faces)
            human_detected = False
            for (x, y, w, h) in face_cascade.detectMultiScale(gray, 1.3, 5):
                human_detected = True
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                # Label the detected human
                label_y = y - 10 if y - 10 > 10 else y + h + 20
                cv2.putText(frame, "Human", (x, label_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

            # Motion detection
            motion_detected = False
            fgMask = backSub.apply(frame)

            # Clean up the mask and find contours
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            fgMask = cv2.morphologyEx(fgMask, cv2.MORPH_OPEN, kernel, iterations=2)

            contours, _ = cv2.findContours(fgMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                if cv2.contourArea(cnt) > min_motion_area:
                    motion_detected = True
                    x, y, w, h = cv2.boundingRect(cnt)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            if motion_detected or human_detected:
                cv2.putText(frame, "Motion/Human Detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                frames_since_last_detection = 0

                # Start recording if not already recording
                if not recording:
                    filename = datetime.datetime.now().strftime("recording_%Y%m%d_%H%M%S.avi")
                    fourcc = cv2.VideoWriter_fourcc(*'XVID')
                    out = cv2.VideoWriter(filename, fourcc, fps, (frame_width, frame_height))
                    recording = True
            else:
                # No detection this frame
                if recording:
                    frames_since_last_detection += 1
                    if frames_since_last_detection > BUFFER_AFTER_DETECTION:
                        # Stop recording
                        recording = False
                        if out is not None:
                            out.release()
                            out = None

            # Write frame to file if currently recording
            if recording and out is not None:
                out.write(frame)

            cv2.imshow("Webcam Feed", frame)

            # Exit when the user presses the 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        # Release resources in any case (Ctrl+C, window closed, etc.)
        cap.release()
        if out is not None:
            out.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
