from multiprocessing import Process


def create_processes(N, function, stop_flag, args_list=None):
    """
    Create a list of processes.

    Parameters:
    N (int): The number of processes to create.
    function (function): The function to be executed by each process.
    stop_flag: Event() to stop the process from the main process.
    args_list (list of lists, optional): Additional arguments for each process. Default is None.

    Returns:
    list: List of processes.
    """
    processes = []
    for i in range(N):
        if args_list:
            p = Process(target=function, args=tuple(args_list[i] + [stop_flag]))
        else:
            p = Process(target=function, args=(stop_flag))
        processes.append(p)

    return processes


def start_processes(processes):
    """
    Start all the processes in the list.

    Parameters:
    processes (list): List of `multiprocessing.Process` objects to start.
    """
    for p in processes:
        p.start()


def wait_processes(processes):
    """
    Wait for all processes in the list to complete execution.

    Parameters:
    processes (list): List of `multiprocessing.Process` objects to wait for.
    """
    for p in processes:
        p.join()
