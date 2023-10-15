import cv2


def capture_frames():
    """
    Capture frames from a camera.

    This function uses OpenCV to capture frames from a camera specified by its index.
    It continuously reads frames from the camera and yields them as byte strings in the format required for streaming.

    Args:
        None.

    Returns:
        Iterator[str]: Yields each frame as a byte string in the format required for streaming.
    """
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
