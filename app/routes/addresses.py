from flask import Blueprint, current_app, request, jsonify
from utils.problem_definiton import detect_address_format
from flask_babel import gettext

# Define a Flask blueprint for handling address-related routes
addresses_blueprint = Blueprint("addresses_blueprint", __name__)


# TODO: CHECK THIS FUNCTION
@addresses_blueprint.route("/handle-address", methods=["POST", "GET"])
def register_address():
    """
    Register an address based on the provided form data. The address can be either a depot or a regular address.
    It converts the all the addresses to coordinates (if necessary).

    Args:
        None

    Returns:
        dict: A dictionary containing the success status, a message, the coordinates, and the index of the registered address.
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
    """
    Updates the problem data when a node is deleted.

    This function removes the given index from the 'start_nodes' and 'end_nodes' lists,
    and removes the corresponding address from the 'addresses' dictionary in the current_app.problem_data.

    Args:
        index (int): The index of the node to be deleted.

    Returns:
        None"""
    if index in current_app.problem_data["start_nodes"]:
        current_app.problem_data["start_nodes"].remove(index)
    if index in current_app.problem_data["end_nodes"]:
        current_app.problem_data["end_nodes"].remove(index)
    current_app.problem_data["addresses"].pop(index)


@addresses_blueprint.route("/delete-address", methods=["POST", "GET"])
def delete_address():
    """
    Delete an address based on the provided form data. The address is identified by its index.

    Args:
        None

    Returns:
        dict: A dictionary with the following keys:
            - success (bool): Indicates whether the address was deleted successfully.
            - message (str): A success message.
            - problem_data (obj): The updated problem data."""
    if request.method == "POST":
        index = int(request.form["index"])
        update_problem_when_deleted(index)
        return jsonify(
            success=True,
            message=gettext("Address deleted successfully"),
            problem_data=current_app.problem_data,
        )
