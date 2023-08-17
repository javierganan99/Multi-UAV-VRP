from flask import current_app, render_template, request, redirect, jsonify, Flask
from app.utils.problem_definiton import AddressFormatConversion
from app.messaging.sockets import VehiclesSocketIO
from app.routes.addresses import addresses_blueprint
from app.routes.loaders import loaders_blueprint
from app.routes.save import save_blueprint
from app.routes.routes import routes_blueprint
from app.routes.simulation import simulation_blueprint
from flask_babel import Babel, gettext
from flask_socketio import SocketIO

app = Flask(__name__, template_folder="app/templates", static_folder="app/static")
app.config.from_object("app.config.Config")


# To get the best matching language
def get_locale():
    return request.accept_languages.best_match(app.config["LANGUAGES"].keys())


babel = Babel(app, locale_selector=get_locale)

# SocketIO to manage the streaming
socketio = SocketIO(app)
vehicles_namespace = VehiclesSocketIO("/vehiclesns")
socketio.on_namespace(vehicles_namespace)
# Save references to the socketio and the vehicles namespace
app.socketio = socketio
app.vehicles_namespace = vehicles_namespace

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


@app.route("/reset", methods=["POST"])
def reset():
    if request.method == "POST":
        current_app.coordinates_list = [
            current_app.coordinates_list[0]
        ]  # Reset coordinates
        current_app.problem_data = {}  # Reset problem definition
        current_app.solver_data = {}  # Reset solver definiton
        return jsonify(success=True, message=gettext("Reset done"))


@app.route("/", methods=["POST", "GET"])
def main():
    # Initialize variables global to the app context
    current_app.coordinates_list = [[37.38602323347123, -5.99311606343879]]
    current_app.converter = AddressFormatConversion(
        app.config["API_KEY"],
        app.config["GEOCODE_API_URL"],
        app.config["DISTANCE_MATRIX_API_URL"],
    )
    current_app.problem_data = {}
    current_app.solver_data = {}
    current_app.routes = {}
    current_app.problem_data["n_vehicles"] = 2
    current_app.simulation = False

    if request.method == "POST":
        try:
            return redirect("/")
        except:
            return gettext("Error introducing the address")
    else:
        API_KEY = app.config["API_KEY"]
        return render_template(
            "index.html",
            coordinates=current_app.coordinates_list,
            apiKey=API_KEY,
        )


if __name__ == "__main__":
    socketio.run(app)
