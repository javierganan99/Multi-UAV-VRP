import math
import time


def calculate_intermediate_coordinate(c1, c2, velocity, timestamp):
    """
    Calculate intermediate coordinate between two locations using the haversine formula,
    based on the velocity of the vehicle and the timestamp.

    Args:
        c1 (tuple): A tuple representing the coordinates of the
            first location in the format (latitude, longitude).
        c2 (tuple): A tuple representing the coordinates of the
            second location in the format (latitude, longitude).
        velocity (float): The velocity of the vehicle in meters per second.
        timestamp (float): The time elapsed in seconds since the start of the journey.

    Returns:
        dict: A dictionary containing the intermediate coordinate as a tuple (latitude, longitude).
    """
    coords = {}
    if len(c1) == 3 and len(c2) == 3:
        lat1, lon1, alt1 = c1
        lat2, lon2, alt2 = c2
    else:
        lat1, lon1 = c1[:2]
        lat2, lon2 = c2[:2]
        alt1, alt2 = None, None
    # Same node singularity
    if c1 == c2:
        coords["lat"] = lat1
        coords["lon"] = lon1
        if alt1 and alt2:
            coords["alt"] = alt1
        return coords
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad
    # Haversine formula
    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    # Radius of Earth
    radius = 6371000
    # Calculate total distance between c1 and c2
    total_distance = radius * c
    # Calculate distance to the intermediate point along the great circle
    intermediate_distance = timestamp / (total_distance / velocity) * total_distance
    # Calculate bearing from c1 to c2
    theta = math.atan2(
        math.sin(delta_lon) * math.cos(lat2_rad),
        math.cos(lat1_rad) * math.sin(lat2_rad)
        - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon),
    )
    # Calculate intermediate point's latitude
    lat_intermediate = math.asin(
        math.sin(lat1_rad) * math.cos(intermediate_distance / radius)
        + math.cos(lat1_rad)
        * math.sin(intermediate_distance / radius)
        * math.cos(theta)
    )
    # Calculate intermediate point's longitude
    lon_intermediate = lon1_rad + math.atan2(
        math.sin(theta) * math.sin(intermediate_distance / radius) * math.cos(lat1_rad),
        math.cos(intermediate_distance / radius)
        - math.sin(lat1_rad) * math.sin(lat_intermediate),
    )
    # Convert intermediate latitude and longitude back to degrees
    coords["lat"] = math.degrees(lat_intermediate)
    coords["lon"] = math.degrees(lon_intermediate)
    if alt1 and alt2:
        # Calculate intermediate point's altitude
        alt_intermediate = alt1 + (alt2 - alt1) * (
            intermediate_distance / total_distance
        )
        coords["alt"] = alt_intermediate
    return coords


class SimulationPath:
    """
    Simulates the UAVs' positions in their corresponding route at the corresponding timestep.
    When iterated, returns the corresponding position
    of each UAV in in the current simulated time.

    Args:
        routes (dict): A dictionary containing the routes for each vehicle,
            with their corresponding nodes and coordinates.
        distance_matrix (list of lists): A matrix containing the distances between nodes.
        timestep (int, optional): The initial timestep for the simulation. Default is 100.
        decrease_factor (float, optional): The factor by which the timestep
            decreases in each iteration. Default is 0.01.

    Attributes:
        initial_timestep (int): The initial timestep for the simulation.
        timestep (int): The current timestep for the simulation.
        decrease_factor (float): The factor by which the simulated
            timestep decreases for the real time to wait.
        routes (dict): A dictionary containing the routes for each vehicle,
            with their corresponding nodes and coordinates.
        number_of_vehicles (int): The number of vehicles in the simulation.
        distance_matrix (list of lists): A matrix containing the distances between nodes.
        cummulative_times (list): A list of lists containing the cumulative times for each route.
        current_node_index (list): A list containing the current node index for each vehicle.
        finish_route (list): A list containing the stop flag for each vehicle's route.
        current_path (list): A list containing the current path coordinates for each vehicle.
        current_coords (list): A list containing the current coordinates of each vehicle.
        time (int): The current simulation time.

    Methods:
        __init__(routes, distance_matrix, timestep=100, decrease_factor=0.01):
            Initializes an instance of the class.
        __iter__(): Returns an iterator object that iterates over the object.
        __next__(): Performs a sleep operation for a specified duration,
            updates the current time, and calculates the current coordinates
            based on the given routes and time.
    """

    def __init__(self, routes, distance_matrix, timestep=100, decrease_factor=0.01):
        """
        It sets the initial timestep, timestep decrease factor, routes,
        number of vehicles, distance matrix, cummulative times, current node index,
        finish route flags, current path, current coordinates, and simulation time.

        Args:
            routes (dict): A dictionary containing the routes for each vehicle,
                with their corresponding nodes and coordinates.
            distance_matrix (list of lists): A matrix containing the distances between nodes.
            timestep (int, optional): The initial timestep for the simulation. Default is 100.
            decrease_factor (float, optional): The factor by which the timestep decreases
                in each iteration. Default is 0.01.

        Returns:
            None"""
        self.initial_timestep = timestep
        self.timestep = timestep
        self.decrease_factor = decrease_factor
        self.routes = routes
        self.number_of_vehicles = len(self.routes.keys())
        self.distance_matrix = distance_matrix
        # Calculate cummulative times for each route
        self.cummulative_times = []
        for index in range(self.number_of_vehicles):
            cummulative_time = [
                self.distance_matrix[self.routes[index]["nodes"][i]][
                    self.routes[index]["nodes"][i + 1]
                ]
                / self.routes[index]["velocity"]
                for i in range(len(self.routes[index]["nodes"][:-1]))
            ]
            cummulative_time = [0] + [
                sum(cummulative_time[: i + 1]) for i in range(len(cummulative_time))
            ]
            self.cummulative_times.append(cummulative_time)
        # Index of the current node for each vehicle
        self.current_node_index = [0] * self.number_of_vehicles
        # Stop flag for the route of each vehicle
        self.finish_route = [False] * self.number_of_vehicles
        # Calculate current coordinates (c1,c2) path in which the vehicle is
        self.current_path = []
        # Calculate the current coordinates of each vehicle
        self.current_coords = []
        for v_idx in self.routes.keys():
            current_coords = [
                self.routes[v_idx]["coordinates"][self.current_node_index[v_idx]],
                self.routes[v_idx]["coordinates"][self.current_node_index[v_idx] + 1],
            ]
            self.current_path.append(current_coords)
            self.current_coords.append(current_coords)
        self.time = 0  # Time to control the simulation

    def __iter__(self):
        return self

    def __next__(self):
        """
        This function performs a sleep operation for a specified duration, updates the current time,
        and calculates the current coordinates based on the given routes and time.
        It iterates through each route, updating the current node index and path if necessary,
        and calculates the intermediate coordinate based on the current time and velocity.

        Args:
            None

        Returns:
            dict: The current coordinates of each route."""
        time.sleep(self.decrease_factor * self.timestep)
        if all(self.finish_route):
            raise StopIteration
        self.timestep = self.initial_timestep
        min_timestep = self.timestep
        for v_idx in self.routes.keys():
            if self.finish_route[v_idx]:
                continue
            if (self.time + self.timestep) > self.cummulative_times[v_idx][
                self.current_node_index[v_idx] + 1
            ]:  # Adapt self.timestep to reach end-path node
                diff = (
                    self.cummulative_times[v_idx][self.current_node_index[v_idx] + 1]
                    - self.time
                )
                if diff < min_timestep:
                    self.timestep = diff
                    min_timestep = self.timestep

            if (  # Next node
                self.time
                == self.cummulative_times[v_idx][self.current_node_index[v_idx] + 1]
            ):
                self.current_node_index[v_idx] += 1
                if (
                    self.current_node_index[v_idx]
                    >= len(self.routes[v_idx]["nodes"]) - 1
                ):
                    self.finish_route[v_idx] = True
                self.current_path[v_idx] = [
                    self.routes[v_idx]["coordinates"][self.current_node_index[v_idx]],
                    self.routes[v_idx]["coordinates"][
                        self.current_node_index[v_idx]
                        + (1 if not self.finish_route[v_idx] else 0)
                    ],
                ]
            current_coordinate = calculate_intermediate_coordinate(
                self.current_path[v_idx][0],
                self.current_path[v_idx][1],
                self.routes[v_idx]["velocity"],
                self.time
                - self.cummulative_times[v_idx][self.current_node_index[v_idx]],
            )
            self.current_coords[v_idx] = current_coordinate
        self.time += self.timestep
        return self.current_coords
