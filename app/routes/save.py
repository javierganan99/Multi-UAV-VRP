from flask import Blueprint, current_app, request, jsonify
from flask_babel import gettext
from app.utils.auxiliary import save_yaml, ensure_exist

# Define a Flask blueprint for handling saving-related routes
save_blueprint = Blueprint("save_blueprint", __name__)


@save_blueprint.route("/save-nodes", methods=["POST"])
def save_nodes(file="output/nodes2visit.yaml"):
    """
    Save the list of addresses (nodes) to visit to a YAML file.

    Parameters:
    file (str, optional): The path of the file to save to. Default is "output/nodes2visit.yaml".
    """
    if request.method == "POST":
        ensure_exist("/".join(file.split("/")[:-1]))
        data = {"addresses": current_app.coordinates_list}
        save_yaml(file, data)
        return jsonify(success=True, message=gettext("Nodes saved"))


@save_blueprint.route("/save-routes", methods=["POST"])
def save_routes(file="output/routes.yaml"):
    """
    Save the generated routes to a YAML file.

    Parameters:
    file (str, optional): The path of the file to save to. Default is "output/routes.yaml".
    """
    if request.method == "POST":
        ensure_exist("/".join(file.split("/")[:-1]))
        data = {"routes": current_app.routes}
        save_yaml(file, data)
        return jsonify(success=True, message=gettext("Routes saved"))


@save_blueprint.route("/travel-mode", methods=["POST"])
def save_travel_mode():
    """
    Save the chosen travel mode to the problem data in the application context.
    """
    if request.method == "POST":
        current_app.problem_data["travel_mode"] = request.form.get("travelmode")
        return jsonify(success=True, message=gettext("Travel mode saved"))
