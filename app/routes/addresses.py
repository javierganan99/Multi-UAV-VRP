"""
AGPL-3.0 License

Author: Francisco Javier Gañán

This module defines routes and functions to handle address-related operations.

It includes the following functionality:

1. Flask Blueprint for managing address-related routes.
2. Functions for registering addresses, updating problem data,
    deleting addresses, and changing altitudes.

Routes:
    - '/handle-address' (POST): Registers an address based on provided form data,
        converting addresses to coordinates if necessary.
    - '/delete-address' (DELETE): Deletes an address identified by its index.
    - '/change-altitude' (PATCH): Changes the altitude of a specified address.

Functions:
    - 'update_problem_when_deleted': Updates problem data when a node is deleted.
"""

from flask import Blueprint, current_app, request, jsonify
from flask_babel import gettext
from utils.problem_definiton import detect_address_format


# Define a Flask blueprint for handling address-related routes
addresses_blueprint = Blueprint("addresses_blueprint", __name__)


# TODO: CHECK THIS FUNCTION
@addresses_blueprint.route("/handle-address", methods=["POST"])
def register_address():
    """
    Register an address based on the provided form data.
    The address can be either a depot or a regular address.
    It converts the all the addresses to coordinates (if necessary).

    Args:
        None

    Returns:
        dict: A dictionary containing the success status, a message, \
        the coordinates, and the index of the registered address.
    """
    if request.method == "POST":
        address = request.form["address"]
        depot = request.form["depot"]
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
        if depot != "false":
            current_app.problem_data["addresses"][0] = coordinates
            return jsonify(
                success=True,
                message=gettext("Depot registered successfully"),
                coordinates=coordinates,
                index=0,
            )
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
    and removes the corresponding address from the 'addresses' dictionary in the \
    current_app.problem_data.

    Args:
        index (int): The index of the node to be deleted.

    Returns:
        None"""
    if index in current_app.problem_data["start_nodes"]:
        current_app.problem_data["start_nodes"].remove(index)
    if index in current_app.problem_data["end_nodes"]:
        current_app.problem_data["end_nodes"].remove(index)
    current_app.problem_data["addresses"].pop(index)


@addresses_blueprint.route("/delete-address", methods=["DELETE"])
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
    if request.method == "DELETE":
        index = int(request.form["index"])
        update_problem_when_deleted(index)
        return jsonify(
            success=True,
            message=gettext("Address deleted successfully"),
            problem_data=current_app.problem_data,
        )


@addresses_blueprint.route("/change-altitude", methods=["PATCH"])
def change_altitude():
    """
    Change the altitude of a specified address.

    Returns a JSON object with the status of the altitude change operation.

    Args:
        index (int): The index of the address whose altitude needs to be changed.
        altitude (float): The new altitude value to be assigned to the address.

    Returns:
        dict: A dictionary containing the status of the altitude change operation.
            - success (bool): Indicates whether the altitude was changed successfully.
            - message (str): A success or error message indicating the operation's status.
    """
    if request.method == "PATCH":
        index = int(request.form["index"])
        try:
            altitude = float(request.form["altitude"])
        except ValueError:
            return jsonify(
                success=False,
                message=gettext("Value could not be parsed to float"),
            )
        if len(current_app.problem_data["addresses"][index]) == 2:
            current_app.problem_data["addresses"][index].append(altitude)
        else:
            current_app.problem_data["addresses"][index][2] = altitude
        return jsonify(
            success=True,
            message=gettext("Altitude changed successfully"),
        )
