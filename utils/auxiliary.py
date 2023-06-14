import yaml
import os
import time


# Decorators
def measure_execution_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time of {func.__name__}: {execution_time:.2f}s.")
        return result

    return wrapper


def load_yaml(file):
    """
    This function loads a yaml file into a dictionary
    """
    assert os.path.exists(file), "File not found in path {}".format(file)
    assert isinstance(file, str) and file.endswith(
        ".yaml"
    ), "Not the proper format, must be a yaml file string variable"
    with open(file, "r") as f:
        params = yaml.safe_load(f)
    return params


# def generate_random_map(area_dims, n_points, depot_coords=[0, 0, 0], max_inspecting_time=300):
#     """
#     Generates a random map, generating n_points in a area of dimensions area_dims[0]*area_dims[1] m^2
#     """
#     points = []
#     points.append(depot_coords)
#     while len(points) < n_points:
#         x = random.randint(-area_dims[0] / 2, area_dims[0] / 2 - 1)
#         y = random.randint(-area_dims[1] / 2, area_dims[1] / 2 - 1)
#         insp_time = random.randint(0, max_inspecting_time)
#         points.append([x, y, insp_time])
#     return np.array(points)


# def generate_distance_matrix(points, vel):
#     """
#     Create the time matrix between nodes (considering also the waiting time a each node)
#     """
#     num_points = len(points)
#     distances = np.zeros((num_points, num_points), dtype=int)
#     for i in range(num_points):
#         for j in range(i + 1, num_points):
#             distance = np.linalg.norm(points[i, :2] - points[j, :2])
#             distances[i, j] = int(distance / vel + points[j, 2])
#             distances[j, i] = int(distance / vel + points[i, 2])
#     return distances.tolist()


# def plot_routes(points, routes):
#     """
#     Plot the map and routes for each vehicle
#     """
#     plt.scatter(points[:, 0], points[:, 1], color="blue", label="Nodes")
#     plt.scatter(points[0, 0], points[0, 1], color="red", label="Depot")
#     for route in routes:
#         plt.plot(points[route, 0], points[route, 1], linestyle="solid")
#     plt.plot()
#     for point in points:
#         x = point[0]
#         y = point[1]
#         plt.text(x + 15, y + 15, str(point[2]), fontsize=10, verticalalignment="center", horizontalalignment="center")
#     plt.xlabel("X [m]")
#     plt.ylabel("Y [m]")
#     plt.title("Generated Routes")
#     plt.legend()
#     plt.grid(True)
#     plt.show()


def generate_n_colors(n):
    from colorsys import hsv_to_rgb

    colors = []
    increment = 360 / n
    for i in range(n):
        hue = int(i * increment)
        rgb = hsv_to_rgb(hue / 360, 1, 1)
        color = f"#{''.join(format(int(c * 255), '02X') for c in rgb)}"
        colors.append(color)
    return colors


def generate_solution(data, manager, routing, solution, coordinates_list):
    """
    Generates a dictionary with the routing data
    """
    print(f"Objective: {solution.ObjectiveValue()}")
    max_route_time = 0
    routes_dict = {}
    routes_dict["routes"] = {}
    routes = []
    # Generate a color for each vehicle route
    colors = generate_n_colors(data["n_vehicles"])
    for vehicle_id in range(data["n_vehicles"]):
        routes_dict["routes"][vehicle_id] = {}
        index = routing.Start(vehicle_id)
        plan_output = "Route for vehicle {}:\n".format(vehicle_id)
        route_time = 0
        nodes = []
        coordinates = []
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            nodes.append(node)
            coordinates.append(coordinates_list[node])
            plan_output += " {} -> ".format(node)
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_time += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
        node = manager.IndexToNode(index)
        nodes.append(node)
        coordinates.append(coordinates_list[node])
        route_mins = route_time // 60
        route_secs = route_time % 60
        plan_output += "{}\n".format(manager.IndexToNode(index))
        plan_output += "Time to complete the route: {}min {}secs\n".format(route_mins, route_secs)
        print(plan_output)
        max_route_time = max(route_time, max_route_time)
        routes.append(nodes)
        # Save route information
        routes_dict["routes"][vehicle_id]["coordinates"] = coordinates
        routes_dict["routes"][vehicle_id]["nodes"] = nodes
        routes_dict["routes"][vehicle_id]["time"] = route_time
        routes_dict["routes"][vehicle_id]["color"] = colors[vehicle_id]
    max_route_mins = max_route_time // 60
    max_route_secs = max_route_time % 60
    routes_dict["total_time"] = max_route_time
    print("Time to complete the longest route: {}min {}secs\n".format(max_route_mins, max_route_secs))
    return routes_dict
