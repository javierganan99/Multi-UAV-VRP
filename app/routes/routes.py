from flask import Blueprint, current_app, request, jsonify
from flask_babel import gettext
from utils.load_parameters import load_solver_configuration, load_problem_definiton
from utils.auxiliary import adapt_solution, string2value
from utils.or_tools_method import find_routes
from utils.problem_definiton import (
    generate_distance_matrix,
    generate_flight_distance_matrix,
)


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
        if not current_app.problem_data:  # Load defaults
            current_app.problem_data = load_problem_definiton()
        check_list = [
            "n_vehicles",
            "max_flight_time",
            "velocity",
            "start_nodes",
            "end_nodes",
        ]
        for name in check_list:
            value = string2value(request.form[name])
            if not value:
                return jsonify(
                    success=False,
                    message=gettext("Error parsing the values of the problem data"),
                )
            current_app.problem_data[name] = value
        current_app.problem_data["travel_mode"] = request.form["travel_mode"]
        # Distance matrix creation
        if "distance_matrix" not in current_app.problem_data.keys():
            if current_app.problem_data["travel_mode"] == "flight":
                current_app.problem_data[
                    "distance_matrix"
                ] = generate_flight_distance_matrix(
                    current_app.problem_data["addresses"]
                )
            else:
                current_app.problem_data["distance_matrix"] = generate_distance_matrix(
                    current_app.problem_data["addresses"],
                    current_app.config["API_KEY"],
                    current_app.config["GEOCODE_API_URL"],
                    current_app.config["DISTANCE_MATRIX_API_URL"],
                    mode=current_app.problem_data["travel_mode"],
                )
        # Route generation
        data, manager, routing, solution = find_routes(
            current_app.problem_data, current_app.solver_data
        )
        current_app.routes = adapt_solution(
            data, manager, routing, solution, current_app.problem_data["addresses"]
        )
        return jsonify(
            success=True,
            message=gettext("Routes created successfully"),
            routes=current_app.routes,
            problem_data=current_app.problem_data,
        )
