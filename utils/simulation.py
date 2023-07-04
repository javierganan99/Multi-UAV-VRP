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
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Radius of Earth
    radius = 6371000

    # Calculate total distance between c1 and c2
    total_distance = radius * c

    # Calculate distance to the intermediate point along the great circle
    intermediate_distance = timestamp / (total_distance / velocity) * total_distance

    # Calculate bearing from c1 to c2
    theta = math.atan2(math.sin(delta_lon) * math.cos(lat2_rad),
                       math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(
                           delta_lon))

    # Calculate intermediate point's latitude
    lat_intermediate = math.asin(math.sin(lat1_rad) * math.cos(intermediate_distance / radius) +
                                 math.cos(lat1_rad) * math.sin(intermediate_distance / radius) * math.cos(theta))

    # Calculate intermediate point's longitude
    lon_intermediate = lon1_rad + math.atan2(
        math.sin(theta) * math.sin(intermediate_distance / radius) * math.cos(lat1_rad),
        math.cos(intermediate_distance / radius) - math.sin(lat1_rad) * math.sin(lat_intermediate))

    # Convert intermediate latitude and longitude back to degrees
    lat_intermediate_deg = math.degrees(lat_intermediate)
    lon_intermediate_deg = math.degrees(lon_intermediate)

    return lat_intermediate_deg, lon_intermediate_deg


class Simulation:
    def __init__(self, routes, distance_matrix, velocity = 10): # TODO: Load velocity from front
        self.routes = routes
        self.distance_matrix = distance_matrix
        self.velocity = velocity

    def __iter__(self):
        return self
    
    def __next__(self):
        pass

    def return_location(self, vehicle_index, timestamp):
        cummulative_time = [self.distance_matrix[i][i+1] for i in self.routes[vehicle_index]["nodes"][:-1]]
        cummulative_time = [0] + [sum(cummulative_time[:i+1]) for i in range(len(cummulative_time))]
        for i, initial in enumerate(cummulative_time):
            if initial <= timestamp <= cummulative_time[i+1]:
                c1 = self.routes[vehicle_index]["coordinates"][i]
                c2 = self.routes[vehicle_index]["coordinates"][i+1]
                return calculate_intermediate_coordinate(c1, c2, self.velocity * 0.277777 , timestamp - initial)
            elif timestamp >= cummulative_time[-1]:
                print("Route ended!")
                return cummulative_time[-1]
                # TODO: Add ending logic




