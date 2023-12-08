"""
AGPL-3.0 License

Author: Francisco Javier Gañán

This module defines routes and functions to handle loading-related operations.

It includes the following functionality:

1. Flask Blueprint for managing loading-related routes.
2. Function for loading problem definition data from a YAML file,
    converting addresses to coordinates, and storing them in the application context.

Routes:
    - '/load-problem' (GET): Loads problem definition data from a YAML file,
        converts addresses to coordinates, and stores them in the application context.
"""

from flask import Blueprint, current_app, request, jsonify
from flask_babel import gettext
from utils.problem_definiton import detect_address_format
from utils.load_parameters import load_problem_definiton

# Define a Flask blueprint for handling loading-related routes
loaders_blueprint = Blueprint("loaders_blueprint", __name__)


@loaders_blueprint.route("/load-problem", methods=["GET"])
def load_yaml_problem():
    """
    Load problem definition data from a YAML file, convert the addresses to coordinates,
        and store them in the application context.

    Args:
        None

    Returns:
        None"""
    coord_inds = []
    if request.method == "GET":
        current_app.problem_data = load_problem_definiton()
        # Addresses to the proper format
        for i, address in enumerate(current_app.problem_data["addresses"]):
            c_format = detect_address_format(address)
            if c_format == "str-coordinates":
                coordinates = address.replace(" ", "").split(",")
            elif c_format == "name":
                coordinates = current_app.converter.address2coords(address)
            else:
                coordinates = address
            if coordinates is None:
                return jsonify(
                    success=False,
                    message=gettext("Failed to convert address"),
                    coordinates=None,
                )
            coordinates = [float(i) for i in coordinates]
            if coordinates not in current_app.problem_data["addresses"]:
                current_app.problem_data["addresses"].append(coordinates)
                idx = len(current_app.problem_data["addresses"]) - 1
            else:
                idx = current_app.problem_data["addresses"].index(coordinates)
            coord_inds.append((coordinates, idx))
            current_app.problem_data["coord_inds"] = coord_inds
        return jsonify(
            success=True,
            message=gettext("Data loaded properly"),
            problem_data=current_app.problem_data,
        )
