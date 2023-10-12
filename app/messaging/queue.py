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