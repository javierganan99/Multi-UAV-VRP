def wait_threads(threads):
    """
    Wait for all threads in the list to complete execution.

    Parameters:
    threads (list): List of `Thread` objects to wait for.
    """
    for t in threads:
        t.join()
