from flask import (
    current_app,
    render_template,
    request,
    redirect,
    jsonify,
    send_from_directory,
    Flask,
)
from utils.problem_definiton import AddressFormatConversion
from app.routes.addresses import addresses_blueprint
from app.routes.loaders import loaders_blueprint
from app.routes.save import save_blueprint
from app.routes.routes import routes_blueprint
from app.routes.simulation import simulation_blueprint
from flask_babel import Babel, gettext

app = Flask(__name__, template_folder="app/templates", static_folder="app/static")
app.config.from_object("app.config.Config")


# To get the best matching language
def get_locale():
    """
    Get the locale that best matches the user's preferred language.

    This function uses the `accept_languages` attribute from the `request` object to determine the best matching locale based on the user's preferred language. It compares the user's preferred language against the available languages defined in the `LANGUAGES` configuration dictionary.

    Returns:
        str: The locale that best matches the user's preferred language."""
    return request.accept_languages.best_match(app.config["LANGUAGES"].keys())


babel = Babel(app, locale_selector=get_locale)

# Blueprint for addresses related routes
app.register_blueprint(addresses_blueprint, url_prefix="")

# Blueprint for loaders
app.register_blueprint(loaders_blueprint, url_prefix="")

# Blueprint for routes to save information
app.register_blueprint(save_blueprint, url_prefix="")

# Blueprint for routes to generate routes
app.register_blueprint(routes_blueprint, url_prefix="")

# Blueprint for routes to manage simulation
app.register_blueprint(simulation_blueprint, url_prefix="")


@app.route("/images/<filename>")
def custom_image(filename):
    """
    This function retrieves and returns a custom image file from the "app/static/images" directory.

    Args:
        filename (str): The name of the image file to be retrieved.

    Returns:
        str: The retrieved custom image file.

    Example:
        >>> custom_image("image.jpg")"""
    return send_from_directory("app/static/images", filename)


@app.route("/reset", methods=["POST"])
def reset():
    """
    Resets the problem definition, solver definiton, and routes.

    This function resets the problem definition, solver definition, and routes by clearing the respective data structures.
    It sets the 'addresses', 'start_nodes', 'end_nodes' to empty lists, and 'n_vehicles' to 1.
    It also sets the 'simulation' flag to False.

    Returns:
        jsonify: A JSON response indicating the success of the reset operation."""
    current_app.problem_data = {}  # Reset problem definition
    current_app.solver_data = {}  # Reset solver definiton
    current_app.routes = {}  # Reset the routes
    current_app.problem_data["addresses"] = []
    current_app.problem_data["start_nodes"] = []
    current_app.problem_data["end_nodes"] = []
    current_app.problem_data["n_vehicles"] = 1
    current_app.simulation = False
    return jsonify(success=True, message=gettext("Reset done"))


@app.route("/", methods=["POST", "GET"])
def main():
    """
    Initialize the main function of the app.

    This function initializes variables global to the app context, sets the map center coordinates,
    sets up an AddressFormatConversion object, and calls the reset function to initialize variables.
    When a POST request is made, the function redirects to the root URL. If an error occurs, it returns an error message.
    Otherwise, it renders the index.html template with the map center coordinates and the API key.

    Args:
        None

    Returns:
        None"""
    current_app.map_center = [
        [37.38602323347123, -5.99311606343879]
    ]  # Center of the map
    current_app.converter = AddressFormatConversion(
        app.config["API_KEY"],
        app.config["GEOCODE_API_URL"],
        app.config["DISTANCE_MATRIX_API_URL"],
    )
    reset()  # Initialize variables

    if request.method == "POST":
        try:
            return redirect("/")
        except:
            return gettext("Error introducing the address")
    else:
        API_KEY = app.config["API_KEY"]
        return render_template(
            "index.html",
            coordinates=current_app.map_center,
            apiKey=API_KEY,
        )


if __name__ == "__main__":
    app.run(host=app.config["APP_HOST"], port=app.config["APP_PORT"])
