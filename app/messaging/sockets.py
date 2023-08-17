import socket
import cv2
import pickle
import struct
import threading
from flask_socketio import Namespace
from app.utils.auxiliary import decompress_frame, compress_frame, buffer2base64
from app.concurrency.threads import wait_threads


class VehiclesSocketIO(Namespace):
    """
    Namespace class for managing Flask-SocketIO communication related to vehicles.
    It emits images to connected clients, and handles connect and disconnect events.
    """

    def on_connect(self):
        print("Vehicle connected")

    def on_disconnect(self):
        print("Vehicle disconnected")

    def emit_image(self, frame, ID):
        """
        Emits an image to the client side.

        Parameters:
        frame: The image to be emitted.
        ID (int): The ID of the vehicle.
        """
        self.emit("image_stream" + str(ID), {"frame": frame, "vehicle_id": ID})


class SocketServer:
    """
    Class for managing a server-side socket.
    It allows to accept client connections, handle client data streams in separate threads, and close the server.
    """

    def __init__(self, host, port):
        """
        Constructor of the SocketServer class. Sets up a socket server at the given host and port.

        Parameters:
        host (str): Host of the server.
        port (int): Port number the server listens to.
        """
        self.threads = []  # List of active threads
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("HOST IP:", host)
        socket_address = (host, port)
        self.server_socket.bind(socket_address)
        self.server_socket.listen()

    def start(self, stop_flag, queues):
        """
        Starts the server. Accepts incoming client connections and handles them in separate threads.

        Parameters:
        stop_flag: A threading.Event() object that indicates when to stop the server.
        queues: A list of queues for storing client data.
        """
        self.server_socket.settimeout(1)  # 1 second timeout
        while not stop_flag.is_set():
            try:
                client_socket, addr = self.server_socket.accept()
                ID = len(self.threads)
                thread = threading.Thread(
                    target=self.stream_client,
                    args=(stop_flag, ID, addr, client_socket, queues),
                )
                self.threads.append(thread)
                self.threads[ID].start()
                print("TOTAL CLIENTS ", len(self.threads))  # Number of threads
            except socket.timeout:
                continue
        wait_threads(self.threads)
        self.close()

    def stream_client(
        self, stop_flag, ID, addr, client_socket, queues, packet_size=4 * 1024
    ):
        """
        Handles a client data stream in a separate thread. Reads packets of data from the client, unpacks and decodes them into frames,
        processes the frames (compresses, encodes), and puts them into a queue.

        Parameters:
        stop_flag: A threading.Event() object that indicates when to stop the client.
        ID (int): The ID of the client.
        addr: Address of the client.
        client_socket: A socket connection object for the client.
        queues: A list of queues for storing client data.
        packet_size (int, optional): The size of each packet of data received from the client. Default is 4 * 1024.
        """
        print("CLIENT {} CONNECTED!".format(addr))
        if client_socket:
            data = b""
            payload_size = struct.calcsize("Q")
            while not stop_flag.is_set():
                while len(data) < payload_size:
                    packet = client_socket.recv(packet_size)
                    if not packet:
                        break
                    data += packet
                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("Q", packed_msg_size)[0]

                while len(data) < msg_size:
                    data += client_socket.recv(packet_size)
                frame_data = data[:msg_size]
                data = data[msg_size:]
                frame = pickle.loads(frame_data)
                frame = decompress_frame(frame)
                # TODO: Add some processing adding the vehicle ID and coordinates!
                buffer = compress_frame(frame)
                frame_encoded = buffer2base64(buffer)
                queues[ID].put(frame_encoded)

    def close(self):
        self.server_socket.close()


class SocketClient:
    """
    Class for managing a client-side socket.
    It allows to connect to a server, send video streams, and close the client.
    """

    def __init__(self, host, port):
        """
        Constructor of the SocketClient class. Sets up a socket client for the given host and port.

        Parameters:
        host (str): Host of the server to connect to.
        port (int): Port number the server listens to.
        """
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))

    def stream_video(self, stop_flag, source=0):
        """
        Streams a video to the server. The video is captured from the given source.

        Parameters:
        stop_flag: A threading.Event() object that indicates when to stop the client.
        TODO: CHANGE THE SOURCE!
        source (int or str, optional): The source of the video. Can be an integer (camera ID) or a string (video file path). Default is 0.
        """
        self.vid = cv2.VideoCapture(source)
        if self.client_socket:
            while not stop_flag.is_set():
                ret, frame = self.vid.read()
                if not ret:
                    print("VIDEO FINISHED!")
                    break
                compressed_frame = compress_frame(frame)
                a = pickle.dumps(compressed_frame)
                message = struct.pack("Q", len(a)) + a
                try:
                    self.client_socket.sendall(message)
                except:
                    # TODO: Raise an error or a warning!
                    break
            self.close()

    def close(self):
        self.client_socket.close()


def create_server_socket(host, port, queues, stop_flag):
    """
    Creates a SocketServer object and starts it.

    Parameters:
    host (str): Host of the server.
    port (int): Port number the server listens to.
    queues: A list of queues for storing client data.
    stop_flag: A threading.Event() object that indicates when to stop the server.
    """
    serverSocket = SocketServer(host, port)
    serverSocket.start(stop_flag, queues)


def create_client_socket(host, port, source, stop_flag):
    """
    Creates a SocketClient object and starts streaming a video to the server.

    Parameters:
    host (str): Host of the server to connect to.
    port (int): Port number the server listens to.
    source (int or str): The source of the video. Can be an integer (camera ID) or a string (video file path).
    stop_flag: A threading.Event() object that indicates when to stop the client.
    """
    clientSocket = SocketClient(host, port)
    clientSocket.stream_video(stop_flag, source)
