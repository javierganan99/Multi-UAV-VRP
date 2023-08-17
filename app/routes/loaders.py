from flask import Blueprint, current_app, request, jsonify
from app.utils.problem_definiton import detect_address_format
from app.utils.load_parameters import load_problem_definiton, load_solver_configuration
from flask_babel import gettext

# Define a Flask blueprint for handling loading-related routes
loaders_blueprint = Blueprint("loaders_blueprint", __name__)


@loaders_blueprint.route("/load-problem", methods=["POST"])
def load_yaml_problem():
    """
    Load problem definition data from a YAML file, convert the addresses to coordinates, and store them in the application context.
    """
    coord_inds = []
    if request.method == "POST":
        file = request.form["file"]
        current_app.problem_data = load_problem_definiton(file)
        for i, address in enumerate(current_app.problem_data["addresses"]):
            format = detect_address_format(address)
            if format == "str-coordinates":
                coordinates = address.replace(" ", "").split(",")
            elif format == "name":
                coordinates = current_app.converter.address2coords(address)
            else:
                coordinates = address
            if coordinates == None:
                return jsonify(
                    success=False,
                    message=gettext("Failed to convert address"),
                    coordinates=None,
                )
            coordinates = [float(i) for i in coordinates]
            if i == 0:
                current_app.coordinates_list[0] = coordinates
                idx = 0
            elif coordinates not in current_app.coordinates_list:
                current_app.coordinates_list.append(coordinates)
                idx = len(current_app.coordinates_list) - 1
            else:
                idx = current_app.coordinates_list.index(coordinates)
            coord_inds.append((coordinates, idx))
            current_app.problem_data["coord_inds"] = coord_inds
        return jsonify(
            success=True,
            message=gettext("Data loaded properly"),
            problem_data=current_app.problem_data,
        )


@loaders_blueprint.route("/load-solver", methods=["POST"])
def load_yaml_solver():
    """
    Load solver configuration data from a YAML file and store them in the application context.
    """
    if request.method == "POST":
        file = request.form["file"]
        current_app.solver_data = load_solver_configuration(file)
        return jsonify(
            success=True,
            message=gettext("Data loaded properly"),
            solver_data=current_app.solver_data,
        )
