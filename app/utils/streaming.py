import cv2


def capture_frames():
    camera = cv2.VideoCapture(0)  # Adjust the camera index as needed

    while True:
        success, frame = camera.read()

        if not success:
            break

        ret, buffer = cv2.imencode(".jpg", frame)
        frame = buffer.tobytes()

        # Yield the frame as a byte string
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

    camera.release()


class Streamer:
    def __init__(self, source):
        # Initialize webcam
        self.camera = cv2.VideoCapture(source)


def process_frame():
    # Read a frame from the webcam
    _, frame = camera.read()

    # Convert the frame to JPEG format
    _, buffer = cv2.imencode(".jpg", frame)
    frame_encoded = base64.b64encode(buffer).decode("utf-8")

    return frame_encoded
