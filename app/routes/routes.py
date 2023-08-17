from flask import Blueprint, current_app, request, jsonify
from flask_babel import gettext
from app.utils.load_parameters import load_solver_configuration
from app.utils.auxiliary import generate_solution
from app.utils.or_tools_method import find_routes
from app.utils.problem_definiton import (
    generate_distance_matrix,
    generate_flight_distance_matrix,
)
from app.utils.simulation import SimulationPath

# Define a Flask blueprint for handling routes-related routes
routes_blueprint = Blueprint("routes_blueprint", __name__)


@routes_blueprint.route("/create-routes", methods=["POST"])
def generate_route():
    """
    Generate a route based on the provided form data and the problem and solver data stored in the application context.
    This includes generating a distance matrix if it doesn't exist, finding routes using OR-Tools, and generating a solution.
    """
    if request.method == "POST":
        if not current_app.solver_data:
            current_app.solver_data = load_solver_configuration()
        current_app.problem_data["n_vehicles"] = int(request.form["n_vehicles"])
        current_app.problem_data["max_flight_time"] = int(
            request.form["max_flight_time"]
        )
        current_app.problem_data["capacity"] = int(request.form["capacity"])
        current_app.problem_data["velocity"] = int(request.form["velocity"])
        # Distance matrix creation
        if "distance_matrix" not in current_app.problem_data.keys():
            if current_app.problem_data["travel_mode"] == "flight":
                current_app.problem_data[
                    "distance_matrix"
                ] = generate_flight_distance_matrix(current_app.coordinates_list)
            else:
                current_app.problem_data["distance_matrix"] = generate_distance_matrix(
                    current_app.coordinates_list,
                    current_app.config["API_KEY"],
                    current_app.config["GEOCODE_API_URL"],
                    current_app.config["DISTANCE_MATRIX_API_URL"],
                    mode=current_app.problem_data["travel_mode"],
                )
        # Route generation
        data, manager, routing, solution = find_routes(
            current_app.problem_data, current_app.solver_data
        )
        current_app.routes = generate_solution(
            data, manager, routing, solution, current_app.coordinates_list
        )
        # TODO: Eliminate, integrate on simulation route
        # simulation_path = SimulationPath(
        #     current_app.routes["routes"],
        #     current_app.problem_data["distance_matrix"],
        #     velocity=10,
        #     timestep=0.1,
        # )
        # for coords in simulation_path:
        #     pass
        return jsonify(
            success=True,
            message=gettext("Routes created successfully"),
            routes=current_app.routes,
        )
