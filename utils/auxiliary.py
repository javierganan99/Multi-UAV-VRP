import yaml
import os
import time
import cv2
import base64
import numpy as np
import re
from typing import Dict


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


def string2value(input_str):
    parts = input_str.split(",")
    parts = [p.strip() for p in parts if p.strip() != ""]
    if len(parts) == 1:
        return int(parts[0])
    elif len(parts) > 1:
        return [int(i) for i in parts]
    else:
        return False


def compress_frame(frame, codec="jpg"):
    """
    Frame compression usin cv2.imencode
    """
    _, compressed_frame = cv2.imencode("." + codec, frame)
    return compressed_frame


def decompress_frame(frame):
    """
    Decompress frame using a chosen codec
    """
    decompressed_frame = cv2.imdecode(frame, cv2.IMREAD_UNCHANGED)
    return decompressed_frame


def buffer2base64(buffer):
    return base64.b64encode(buffer).decode("utf-8")


def base642image(base64_string):
    """
    The base64_to_image function accepts a base64 encoded string and returns an image
    """
    image_bytes = base64.b64decode(base64_string)
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    return image


def load_yaml(file: str = "data.yaml") -> Dict:
    """
    Load a YAML file into a dictionary.

    Args:
        file (str): Path to the YAML file (default is "data.yaml").

    Returns:
        Dict: Dictionary containing the contents of the YAML file.
    """
    assert os.path.exists(file), "File not found in path {}".format(file)
    assert isinstance(file, str) and file.endswith(
        ".yaml"
    ), "Not the proper format, must be a yaml file string variable"
    with open(file, errors="ignore", encoding="utf-8") as f:
        s = f.read()  # string
        # Remove special characters
        if not s.isprintable():
            s = re.sub(
                r"[^\x09\x0A\x0D\x20-\x7E\x85\xA0-\uD7FF\uE000-\uFFFD\U00010000-\U0010ffff]+",
                "",
                s,
            )
        params = yaml.safe_load(s)
    return params


def save_yaml(file, data):
    """
    This function save data in a yaml file
    """
    with open(file, "w") as file:
        yaml.dump(data, file)


def ensure_folder_exist(path):
    path = str(path)
    separated = path.split(os.path.sep)
    # To consider absolute paths
    if separated[0] == "":
        separated.pop(0)
        separated[0] = os.path.sep + separated[0]
    exists = True
    for f in range(len(separated)):
        path = (
            os.path.sep.join(separated[: f + 1])
            if f > 0
            else (separated[0] + os.path.sep)
        )
        if not os.path.exists(path):
            os.mkdir(path)
            exists = False
    return exists


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


def adapt_solution(data, manager, routing, solution, coordinates_list):
    """
    Generates a dictionary with the routing data
    """
    # TODO: SOLVE LAST PATH COMPUTATION!
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
        route_dist = 0
        nodes = []
        coordinates = []
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            nodes.append(node)
            coordinates.append(coordinates_list[node])
            plan_output += " {} -> ".format(node)
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_dist += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id
            )
        node = manager.IndexToNode(index)
        nodes.append(node)
        coordinates.append(coordinates_list[node])
        velocity = data["velocity"][vehicle_id] * 0.2777777778
        route_time = int(route_dist / velocity)
        route_mins = route_time // 60
        route_secs = route_time % 60
        plan_output += "{}\n".format(manager.IndexToNode(index))
        plan_output += "Time to complete the route: {}min {}secs\n".format(
            route_mins, route_secs
        )
        print(plan_output)
        max_route_time = max(route_time, max_route_time)
        routes.append(nodes)
        # Save route information
        routes_dict["routes"][vehicle_id]["coordinates"] = coordinates
        routes_dict["routes"][vehicle_id]["nodes"] = nodes
        routes_dict["routes"][vehicle_id]["time"] = route_time
        routes_dict["routes"][vehicle_id]["color"] = colors[vehicle_id]
        routes_dict["routes"][vehicle_id]["velocity"] = velocity
        print(velocity)
    max_route_mins = max_route_time // 60
    max_route_secs = max_route_time % 60
    routes_dict["total_time"] = max_route_time
    print(
        "Time to complete the longest route: {}min {}secs\n".format(
            max_route_mins, max_route_secs
        )
    )
    return routes_dict
