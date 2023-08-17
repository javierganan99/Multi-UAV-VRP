import pika
import json
import time
import queue


class RTQueue(queue.Queue):
    """
    Real-Time Queue Class that inherits from queue.Queue.
    This class overrides the put method to remove the oldest item when the queue is full.
    """

    def __init__(self, maxsize=1):
        super().__init__(maxsize)

    def put(self, item, block=True, timeout=None):
        """
        Overrides the put method of the superclass. If the queue size has reached maxsize, discards the oldest item.

        Parameters:
        item: The item to be added to the queue.
        block (bool, optional): Whether to block if necessary until a free slot is available. Default is True.
        timeout (float or None, optional): How long to wait for a free slot. Default is None.
        """
        if self.maxsize > 0 and self.qsize() == self.maxsize:
            self.get()  # Discard the oldest item
        super().put(item, block, timeout)


class RabbitMQueue:
    """
    Class for managing RabbitMQ queues.
    It allows to create, send messages to, and get messages from a RabbitMQ queue.
    It also implements the iterator protocol, allowing to iterate over the messages in the queue.
    """

    def __init__(self, IP="localhost", frequency=1):
        """
        Constructor of the RabbitMQueue class. Sets up a connection and a channel to a RabbitMQ server.

        Parameters:
        IP (str, optional): IP address of the RabbitMQ server. Default is "localhost".
        frequency (int, optional): Frequency of retrieving messages from the queue. Default is 1.
        """
        self.IP = IP
        self.frequency = frequency
        # Connect to RabbitMQ
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters("localhost")
        )
        self.channel = self.connection.channel()

    def __iter__(self):
        return self

    def __next__(self):
        """
        Defines the iteration behavior for the class. Retrieves a message from the RabbitMQ queue, decodes it, waits for a time period (inverse of frequency), and returns it.
        """
        method_frame, _, body = self.channel.basic_get(queue=self.name, auto_ack=True)
        if method_frame:
            message_data = json.loads(body)
            time.sleep(1 / self.frequency)
            return message_data
        else:
            return None

    def create_queue(self, name):
        """
        Creates a new queue in the RabbitMQ server.

        Parameters:
        name (str): Name of the new queue.
        """
        self.name = name
        self.channel.queue_declare(queue=self.name)

    def send(self, message):
        """
        Sends a message to the RabbitMQ queue.

        Parameters:
        message: The message to be sent.
        """
        self.channel.basic_publish(exchange="", routing_key=self.name, body=message)

    def get(self):
        """
        Retrieves the last message from the RabbitMQ queue and returns it.
        """
        # Retrieve the last message of the queue
        method_frame, _, body = self.channel.basic_get(queue=self.name, auto_ack=True)
        if method_frame:
            message_data = json.loads(body)
            return message_data
        else:
            return None

    def __del__(self):
        """
        Destructor of the RabbitMQueue class. Closes the connection to the RabbitMQ server.
        """
        print("Closing!!")
        self.connection.close()
