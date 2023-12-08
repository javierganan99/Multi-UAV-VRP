"""
AGPL-3.0 License

Author: Francisco Javier Gañán

This module defines routes and functions for handling simulation-related operations.

It includes the following functionality:

1. Flask Blueprint for managing simulation-related routes.
2. Functions for starting and stopping a simulation of the vehicle routing problem.

Routes:
    - '/simulation' (GET):
        Starts a simulation of the vehicle routing problem and streams simulated data.
    - '/stop-simulation' (DELETE):
        Activates the flag to end the ongoing simulation of the vehicles.
"""

import json
from flask import Blueprint, current_app, request, jsonify, Response
from flask_babel import gettext
from utils.simulation import SimulationPath

# Define a Flask blueprint for handling simulation-related routes
simulation_blueprint = Blueprint("simulation_blueprint", __name__)


@simulation_blueprint.route("/simulation")
def start_simulation():
    """
    Start a simulation of the vehicle routing problem.

    Returns:
        Response: A response object containing the simulated data."""

    def stream(simulation, simulation_path):
        while simulation:
            try:
                coords = next(simulation_path)
                string_data = f"data: {json.dumps(coords)}\n\n"
                yield string_data
            except StopIteration:
                yield "data: None\n\n"

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


@simulation_blueprint.route("/stop-simulation", methods=["DELETE"])
def stop_simulation():
    """
    Activate the flag to end the ongoing simulation of the vehicles."""
    if request.method == "DELETE":
        current_app.simulation = False
        return jsonify(success=True, message=gettext("Ending simulation..."))
