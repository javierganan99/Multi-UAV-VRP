from flask import Blueprint, current_app, request, jsonify
from flask_babel import gettext
from utils.auxiliary import save_yaml, ensure_folder_exist

# Define a Flask blueprint for handling saving-related routes
save_blueprint = Blueprint("save_blueprint", __name__)


@save_blueprint.route("/save-nodes", methods=["POST"])
def save_nodes(file="output/nodes2visit.yaml"):
    """
    Save the list of addresses (nodes) to visit to a YAML file.

    Parameters:
        file (str, optional): The path of the file to save to. Default is "output/nodes2visit.yaml".

    Returns:
        type: Description of the return param."""
    if request.method == "POST":
        ensure_folder_exist("/".join(file.split("/")[:-1]))
        data = {"addresses": current_app.problem_data["addresses"]}
        save_yaml(file, data)
        return jsonify(success=True, message=gettext("Nodes saved"))


@save_blueprint.route("/save-routes", methods=["POST"])
def save_routes(file="output/routes.yaml"):
    """
    Save the generated routes to a YAML file.

    Parameters:
        file (str, optional): The path of the file to save to. Default is "output/routes.yaml".

    Returns:
        None"""
    if request.method == "POST":
        ensure_folder_exist("/".join(file.split("/")[:-1]))
        data = {"routes": current_app.routes}
        save_yaml(file, data)
        return jsonify(success=True, message=gettext("Routes saved"))
