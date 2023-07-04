import pika
import json
import time

class Queue:
    def __init__(self, IP="localhost", frecuency = 1):
        self.IP = IP
        self.frecuency = frecuency
        # Connect to RabbitMQ
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()

    def __iter__(self):
         return self
    
    def __next__(self):
        method_frame, _, body = self.channel.basic_get(queue=self.name, auto_ack=True)
        if method_frame:
            message_data = json.loads(body)
            time.sleep(1/self.frecuency)
            return message_data
        else:
            return None
    
    def create_queue(self, name):
        self.name = name 
        self.channel.queue_declare(queue=self.name)

    def send(self, message):
            self.channel.basic_publish(exchange='', routing_key=self.name, body=message)

    def get(self):
        # Retrieve the last message of the queue
        method_frame, _, body = self.channel.basic_get(queue=self.name, auto_ack=True)
        if method_frame:
            message_data = json.loads(body)
            return message_data
        else:
            return None

    def __del__(self):
        print("Closing!!")
        self.connection.close()
