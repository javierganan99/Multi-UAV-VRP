from flask import Blueprint, current_app, request, jsonify
from app.utils.problem_definiton import detect_address_format
from flask_babel import gettext

# Define a Flask blueprint for handling address-related routes
addresses_blueprint = Blueprint("addresses_blueprint", __name__)


# TODO: Add node
@addresses_blueprint.route("/handle-address", methods=["POST", "GET"])
def register_address():
    """
    Register an address based on the provided form data. The address can be either a depot or a regular address.
    It converts the all the addresses to coordinates (if necessary).
    """
    if request.method == "POST":
        address = request.form["address"]
        depot = request.form["depot"]
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
        if depot != "false":
            current_app.problem_data["addresses"][0] = coordinates
            return jsonify(
                success=True,
                message=gettext("Depot registered successfully"),
                coordinates=coordinates,
                index=0,
            )
        else:
            if coordinates not in current_app.problem_data["addresses"]:
                current_app.problem_data["addresses"].append(coordinates)
                index = len(current_app.problem_data["addresses"]) - 1
            else:
                index = current_app.problem_data["addresses"].index(coordinates)
            return jsonify(
                success=True,
                message=gettext("Address registered successfully"),
                coordinates=coordinates,
                index=index,
            )


def update_problem_when_deleted(index):
    if index in current_app.problem_data["start_nodes"]:
        current_app.problem_data["start_nodes"].remove(index)
    if index in current_app.problem_data["end_nodes"]:
        current_app.problem_data["end_nodes"].remove(index)
    print(len(current_app.problem_data["addresses"]))
    current_app.problem_data["addresses"].pop(index)


@addresses_blueprint.route("/delete-address", methods=["POST", "GET"])
def delete_address():
    """
    Delete an address based on the provided form data. The address is identified by its index.
    """
    if request.method == "POST":
        index = int(request.form["index"])
        update_problem_when_deleted(index)
        return jsonify(
            success=True,
            message=gettext("Address deleted successfully"),
            problem_data=current_app.problem_data,
        )
