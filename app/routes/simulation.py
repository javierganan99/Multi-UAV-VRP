from flask import Blueprint, current_app, request, jsonify, Response
from flask_babel import gettext
from utils.simulation import SimulationPath
import json

# Define a Flask blueprint for handling simulation-related routes
simulation_blueprint = Blueprint("simulation_blueprint", __name__)


@simulation_blueprint.route("/simulation")
def start_simulation(HOST="localhost", PORT=999):
    """
    TODO: Provide a more insightful description!
    Start a simulation of the vehicle routing problem. This includes creating a server socket thread,
    creating client socket processes, and emitting images from the vehicles to the client side.

    Parameters:
    HOST (str, optional): Host of the server. Default is "localhost".
    PORT (int, optional): Port number the server listens to. Default is 999.
    """

    def stream(simulation, simulation_path):
        while simulation:
            try:
                coords = next(simulation_path)
                string_data = f"data: {json.dumps(coords)}\n\n"
                yield string_data
            except StopIteration:
                return "data: None\n\n"

    current_app.simulation = True
    # Define simulation path
    simulation_path = SimulationPath(
        current_app.routes["routes"],
        current_app.problem_data["distance_matrix"],
        timestep=current_app.problem_data["simulation_time_step"],
        decrease_factor=current_app.problem_data["simulation_time_step_factor"],
    )
    return Response(
        stream(current_app.simulation, simulation_path),
        mimetype="text/event-stream",
    )


@simulation_blueprint.route("/stop-simulation", methods=["POST"])
def stop_simulation():
    """
    Activate the flag to end the ongoing simulation of the vehicles.
    """
    if request.method == "POST":
        current_app.simulation = False
        return jsonify(success=True, message=gettext("Ending simulation..."))
