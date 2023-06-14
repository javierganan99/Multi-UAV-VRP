from flask import Flask, render_template, url_for, request, redirect, jsonify
import signal
from utils.load_parameters import load_problem_definiton, load_solver_configuration
from utils.auxiliary import generate_solution
from utils.or_tools_method import find_routes
from utils.problem_definiton import detect_address_format, generate_distance_matrix, AddressFormatConversion

app = Flask(__name__)
coordinates_list = [[37.38602323347123, -5.99311606343879]]
converter = AddressFormatConversion()
problem_data = {}
solver_data = {}


@app.route("/handle-address", methods=["POST", "GET"])
def register_address():
    global coordinates_list
    if request.method == "POST":
        address = request.form["address"]
        depot = request.form["depot"]
        format = detect_address_format(address)
        if format == "str-coordinates":
            coordinates = address.replace(" ", "").split(",")
        elif format == "name":
            coordinates = converter.address2coords(address)
        if coordinates == None:
            return jsonify(success=False, message="Failed to convert address", coordinates=None)
        coordinates = [float(i) for i in coordinates]
        if depot != "false":
            coordinates_list[0] = coordinates
            return jsonify(
                success=True,
                message="Depot registered successfully",
                coordinates=coordinates,
                index=0,
            )
        else:
            if coordinates not in coordinates_list:
                coordinates_list.append(coordinates)
                index = len(coordinates_list) - 1
            else:
                index = coordinates_list.index(coordinates)
            return jsonify(
                success=True,
                message="Address registered successfully",
                coordinates=coordinates,
                index=index,
            )


@app.route("/delete-address", methods=["POST", "GET"])
def delete_address():
    global coordinates_list
    if request.method == "POST":
        index = int(request.form["index"])
        if coordinates_list and index != 0:
            coordinates_list.pop(index)
        return jsonify(
            success=True,
            message="Address deleted successfully",
            coordinates=coordinates_list,
        )


@app.route("/create-routes", methods=["POST"])
def generate_route():
    global problem_data
    global solver_data
    if request.method == "POST":
        if not solver_data:
            solver_data = load_solver_configuration()
        problem_data["n_vehicles"] = int(request.form["n_vehicles"])
        problem_data["max_flight_time"] = int(request.form["max_flight_time"])
        problem_data["capacity"] = int(request.form["capacity"])
        problem_data["velocity"] = int(request.form["velocity"])
        # Distance matrix creation
        if "distance_matrix" not in problem_data.keys():
            problem_data["distance_matrix"] = generate_distance_matrix(coordinates_list)
        # Route generation
        data, manager, routing, solution = find_routes(problem_data, solver_data)
        routes = generate_solution(data, manager, routing, solution, coordinates_list)
        return jsonify(success=True, message="Routes created successfully", routes=routes)


@app.route("/load-problem", methods=["POST"])
def load_yaml_problem():
    global problem_data
    if request.method == "POST":
        file = request.form["file"]
        problem_data = load_problem_definiton(file)
        return jsonify(success=True, message="Data loaded properly", problem_data=problem_data)


@app.route("/load-solver", methods=["POST"])
def load_yaml_solver():
    global solver_data
    if request.method == "POST":
        file = request.form["file"]
        solver_data = load_solver_configuration(file)
        print(solver_data)
        return jsonify(success=True, message="Data loaded properly", solver_data=solver_data)


@app.route("/reset", methods=["POST"])
def reset():
    global coordinates_list
    global problem_data
    global solver_data
    if request.method == "POST":
        coordinates_list = [coordinates_list[0]]  # Reset coordinates
        problem_data = {}  # Reset problem definition
        solver_data = {}  # Reset solver definiton
        return jsonify(success=True, message="Reset done")


@app.route("/", methods=["POST", "GET"])
def main():
    if request.method == "POST":
        try:
            return redirect("/")
        except:
            return "Error introducing the address"
    else:
        return render_template("index.html", coordinates=coordinates_list)
    # # To control termination
    # def termination_handler(signum, frame):
    #     exit(1)

    # signal.signal(signal.SIGINT, termination_handler)

    # # Define the problem
    # problem_data = load_problem_definiton()
    # # Define the solver configuration
    # solver_data = load_solver_configuration()
    # # Find the routes
    # data, manager, routing, solution = find_routes(problem_data, solver_data)

    # # Print solution
    # if solution:
    #     print_solution(data, manager, routing, solution)
    # else:
    #     print("No solution found!")


if __name__ == "__main__":
    app.run(debug=True)
