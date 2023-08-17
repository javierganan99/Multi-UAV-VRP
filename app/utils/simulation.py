import math


def calculate_intermediate_coordinate(c1, c2, velocity, timestamp):
    """
    Calculate intermediate coordinate between two locations using the haversine formula,
    based on the velocity of the vehicle and the timestamp.
    c1 and c2 are tuples in the format (latitude, longitude).
    velocity is the velocity of the vehicle in meters per second.
    timestamp is the time elapsed in seconds since the start of the journey.
    Returns the intermediate coordinate as a tuple (latitude, longitude).
    """

    lat1, lon1 = c1
    lat2, lon2 = c2

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
    lat_intermediate_deg = math.degrees(lat_intermediate)
    lon_intermediate_deg = math.degrees(lon_intermediate)

    return lat_intermediate_deg, lon_intermediate_deg


class SimulationPath:
    def __init__(self, routes, distance_matrix, velocity=10, timestep=100):
        self.timestep = timestep
        self.routes = routes
        self.number_of_vehicles = len(self.routes.keys())
        self.distance_matrix = distance_matrix
        self.velocity = velocity
        # Calculate cummulative times for each route
        self.cummulative_times = []
        for index in range(self.number_of_vehicles):
            print(self.routes[index]["nodes"])
            cummulative_time = [
                self.distance_matrix[self.routes[index]["nodes"][i]][
                    self.routes[index]["nodes"][i + 1]
                ]
                for i in range(len(self.routes[index]["nodes"][:-1]))
            ]
            cummulative_time = [0] + [
                sum(cummulative_time[: i + 1]) for i in range(len(cummulative_time))
            ]
            self.cummulative_times.append(cummulative_time)
        # Index of the current node for each vehicle
        self.current_node_index = [0] * self.number_of_vehicles
        # Calculate current coordinates (c1,c2) path in which the vehicle is
        self.current_path = []
        for v_idx in range(self.number_of_vehicles):
            self.current_path.append(
                [
                    self.routes[v_idx]["coordinates"][self.current_node_index[v_idx]],
                    self.routes[v_idx]["coordinates"][
                        self.current_node_index[v_idx] + 1
                    ],
                ]
            )
        self.time = 0  # Time to control the simulation

    def __iter__(self):
        return self

    def __next__(self):
        for v_idx in range(self.number_of_vehicles):
            if (
                self.time
                > self.cummulative_times[v_idx][self.current_node_index[v_idx] + 1]
            ):
                self.current_node_index[v_idx] += 1
                self.current_path[v_idx] = [
                    self.routes[v_idx]["coordinates"][self.current_node_index[v_idx]],
                    self.routes[v_idx]["coordinates"][
                        self.current_node_index[v_idx] + 1
                    ],
                ]
            current_coordinate = calculate_intermediate_coordinate(
                self.current_path[v_idx][0],
                self.current_path[v_idx][1],
                self.velocity * 0.277777,
                self.time
                - self.cummulative_times[v_idx][self.current_node_index[v_idx]],
            )
            print(
                "Current coordinate for vehicle {}: {}".format(
                    v_idx, current_coordinate
                )
            )
        print("#############################################################")
        self.time += self.timestep

    def return_location(self, vehicle_index, timestamp):
        for i, initial in enumerate(self.cummulative_times[vehicle_index]):
            if initial <= timestamp <= self.cummulative_times[vehicle_index][i + 1]:
                c1 = self.routes[vehicle_index]["coordinates"][i]
                c2 = self.routes[vehicle_index]["coordinates"][i + 1]
                return calculate_intermediate_coordinate(
                    c1, c2, self.velocity * 0.277777, timestamp - initial
                )
            elif timestamp >= self.cummulative_times[vehicle_index][-1]:
                print("Route ended!")
                return self.cummulative_times[vehicle_index][-1]
                # TODO: Add ending logic
