#!/usr/bin/env python
from messaging.queue import Queue
import json


def main():
    # Create an instance of the Queue class
    print("STARTING!!!")
    queue = Queue()

    # Create a queue
    queue.create_queue("my_queue")

    # Send a message
    message = {
        'key1': 'value1',
        'key2': 'value2'
    }

    queue.send(json.dumps(message))

    # Get the last message in the queue
    while True:
        last_message = queue.get()
        if last_message:
            print("Last Message:", last_message)
        else:
            print("No message available in the queue.")

if __name__ == "__main__":
    main()