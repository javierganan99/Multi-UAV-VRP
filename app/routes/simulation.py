from flask import Blueprint, current_app, request, jsonify
from flask_babel import gettext
from app.messaging.sockets import create_client_socket, create_server_socket
from app.concurrency.processes import create_processes, start_processes, wait_processes
import threading
from multiprocessing import Event
from app.messaging.queue import RTQueue

# Define a Flask blueprint for handling simulation-related routes
simulation_blueprint = Blueprint("simulation_blueprint", __name__)


@simulation_blueprint.route("/start-simulation", methods=["POST"])
def start_simulation(HOST="localhost", PORT=999):
    """
    TODO: Provide a more insightful description!
    Start a simulation of the vehicle routing problem. This includes creating a server socket thread,
    creating client socket processes, and emitting images from the vehicles to the client side.

    Parameters:
    HOST (str, optional): Host of the server. Default is "localhost".
    PORT (int, optional): Port number the server listens to. Default is 999.
    """
    if request.method == "POST":
        current_app.simulation = True
        image_queues = [
            RTQueue() for _ in range(current_app.problem_data["n_vehicles"])
        ]  # To store the images received by the vehicles
        stop_event = Event()  # To stop the server thread and the client processes
        # Create server socket process to add images of the vehicles to the queue
        server_socket_producer = threading.Thread(
            target=create_server_socket,
            args=(HOST, PORT, image_queues, stop_event),
            daemon=True,
        )
        server_socket_producer.start()
        # TODO: Change the sources
        client_processes = create_processes(
            current_app.problem_data["n_vehicles"],
            create_client_socket,
            stop_flag=stop_event,
            args_list=[
                *[
                    [HOST, PORT, r"C:\Users\a907303\GitHub\VRP\videos\newzeland.mp4"]
                    for i in range(current_app.problem_data["n_vehicles"] - 1)
                ],
                [HOST, PORT, 0],
            ],
        )

        # We start the processes
        start_processes(client_processes)

        while current_app.simulation:
            for i in range(current_app.problem_data["n_vehicles"]):
                current_app.vehicles_namespace.emit_image(image_queues[i].get(), i)
                image_queues[i].task_done()
        stop_event.set()
        # Wait for the client processes
        wait_processes(client_processes)
        # We for the server thread
        server_socket_producer.join()
        return jsonify(success=True, message=gettext("Simulation ended!"))


@simulation_blueprint.route("/stop-simulation", methods=["POST"])
def stop_simulation():
    """
    Activate the flag to end the ongoing simulation of the vehicles.
    """
    if request.method == "POST":
        current_app.simulation = False
        return jsonify(success=True, message=gettext("Ending simulation..."))
