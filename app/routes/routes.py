"""
AGPL-3.0 License

Author: Francisco Javier Gañán

This module defines routes and functions for handling route-related operations.

It includes the following functionality:

1. Flask Blueprint for managing routes-related routes.
2. Function for generating a route based on provided form data 
    and the problem and solver data stored in the application context.

Routes:
    - '/create-routes' (POST): Generates a route based on the provided form data
        and the problem and solver data stored in the application context.
        This includes generating a distance matrix if it doesn't exist,
        finding routes using OR-Tools, and generating a solution.
"""

from flask import Blueprint, current_app, request, jsonify
from flask_babel import gettext
from utils.load_parameters import load_solver_configuration, load_problem_definiton
from utils.auxiliary import adapt_solution, string2list
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
    Generate a route based on the provided form data and the
    problem and solver data stored in the application context.
    This includes generating a distance matrix if it doesn't exist,
    finding routes using OR-Tools, and generating a solution.

    Returns:
        JSON object: A JSON object containing the success status,
            a message, the generated routes, and the problem data.
    """
    if request.method == "POST":
        if not current_app.solver_data:
            current_app.solver_data = load_solver_configuration()
        default_problem_data = load_problem_definiton()
        check_list = [
            "n_vehicles",
            "max_flight_time",
            "velocity",
            "start_nodes",
            "end_nodes",
        ]
        new_problem_data = {}
        for name in check_list:
            value = string2list(request.form[name])
            if not value:
                return jsonify(
                    success=False,
                    message=gettext("Error parsing the values of the problem data"),
                )
            new_problem_data[name] = value if name != "n_vehicles" else value[0]
        new_problem_data["addresses"] = current_app.problem_data["addresses"]
        new_problem_data["travel_mode"] = request.form["travel_mode"]
        # Overwrite default problem data
        current_app.problem_data = {**default_problem_data, **new_problem_data}
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
