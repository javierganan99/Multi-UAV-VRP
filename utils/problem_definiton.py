import json
import urllib.request
from unidecode import unidecode
import numpy as np
import math


def calculate_haversine_distance(c1, c2):
    """
    Calculate distance between 2 coordinates using haversine formula.
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
    # Radius of earth
    radius = 6371000
    return radius * c


def generate_flight_distance_matrix(coordinates):
    """
    Create distance matrix using haversine formula
    """
    num_coordinates = len(coordinates)
    distance_matrix = [[0] * num_coordinates for _ in range(num_coordinates)]

    for i in range(num_coordinates):
        for j in range(i + 1, num_coordinates):
            distance = calculate_haversine_distance(coordinates[i], coordinates[j])
            distance_matrix[i][j] = distance
            distance_matrix[j][i] = distance

    return distance_matrix


def generate_distance_matrix(
    addresses,
    API_KEY,
    GEOCODE_API_URL,
    DISTANCE_MATRIX_API_URL,
    mode="walking",
    max_elements=10,
):
    """
    Generate a distance matrix of the specified addresses.
    """
    available_modes = ["driving", "walking", "bicycling", "transit", "flight"]
    assert mode in available_modes, "Distance request mode not available!"

    def build_distance_matrix(response):
        distance_matrix = []
        for row in response["rows"]:
            row_list = [
                row["elements"][j]["distance"]["value"]
                for j in range(len(row["elements"]))
            ]
            distance_matrix.append(row_list)
        return np.array(distance_matrix)

    def fill_matrix(i, j, fullmatrix, submatrix):
        fullmatrix[
            i : i + np.shape(submatrix)[0], j : j + np.shape(submatrix)[1]
        ] = submatrix
        return fullmatrix

    send_request = DistanceMatrixRequest(
        mode=mode,
        API_KEY=API_KEY,
        GEOCODE_API_URL=GEOCODE_API_URL,
        DISTANCE_MATRIX_API_URL=DISTANCE_MATRIX_API_URL,
    )  # To perform request to Distance Matrix API
    num_addresses = len(addresses)
    max_rows = min(num_addresses, max_elements)
    if num_addresses < max_elements:
        q = 1
        r = 0
    else:
        q, r = divmod(num_addresses, max_elements)
    distance_matrix = np.zeros((num_addresses, num_addresses))
    rest = 1 if r > 0 else 0
    ind_row = 0
    for i in range(q + rest):
        origin_addresses = addresses[
            i * max_rows : min((i + 1) * max_rows, num_addresses)
        ]
        ind_col = 0
        for j in range(q + rest):
            dest_addresses = addresses[
                j * max_rows : min((j + 1) * max_rows, num_addresses)
            ]
            response = send_request(origin_addresses, dest_addresses)
            if response is None:
                raise Exception("The distance matrix could not be calculated!")
            submatrix = build_distance_matrix(response)
            distance_matrix = fill_matrix(ind_row, ind_col, distance_matrix, submatrix)
            ind_col += len(submatrix[0])
        ind_row += len(submatrix)
    distance_matrix = distance_matrix.astype(int)
    return distance_matrix.tolist()


def detect_address_format(address: str):
    if (
        isinstance(address, list)
        and isinstance(address[0], (float, int))
        and isinstance(address[1], (float, int))
    ):
        return "float-coordinates"
    address = address.replace(" ", "").split(",")
    if (
        isinstance(address, list)
        and isinstance(address[0], (float, int))
        and isinstance(address[1], (float, int))
    ):
        return "str-coordinates"
    else:
        return "name"


class AddressFormatConversion:
    def __init__(self, API_KEY, GEOCODE_API_URL, DISTANCE_MATRIX_API_URL):
        self.API_KEY, self.GEOCODE_API_URL, self.DISTANCE_MATRIX_API_URL = (
            API_KEY,
            GEOCODE_API_URL,
            DISTANCE_MATRIX_API_URL,
        )

    def address2coords(self, address):
        """
        Given an address in str format, return its coordinates
        """
        address = unidecode(address)
        jsonResult = urllib.request.urlopen(
            self.GEOCODE_API_URL
            + "address="
            + address.replace(" ", "+")
            + "&key="
            + self.API_KEY
        ).read()
        response = json.loads(jsonResult)
        if not response["results"]:
            print("Address {} can not be geocoded! Check it.".format(address))
            return None
        return [
            float(response["results"][0]["geometry"]["location"]["lat"]),
            float(response["results"][0]["geometry"]["location"]["lng"]),
        ]


class DistanceMatrixRequest:
    """
    Build and send request for the given origin and destination addresses.
    First convert the addresses/coordinates into place ids and then perform the distance request
    """

    def __init__(
        self, API_KEY, GEOCODE_API_URL, DISTANCE_MATRIX_API_URL, mode="DRIVING"
    ):
        self.API_KEY, self.GEOCODE_API_URL, self.DISTANCE_MATRIX_API_URL = (
            API_KEY,
            GEOCODE_API_URL,
            DISTANCE_MATRIX_API_URL,
        )
        self.mode = mode
        self.available_modes = ["driving", "walking", "bicycling", "transit"]
        assert mode in self.available_modes, "Distance request mode not available!"

    def __build_address_str(self, address):
        jsonResult = urllib.request.urlopen(
            self.GEOCODE_API_URL
            + "address="
            + address.replace(" ", "+")
            + "&key="
            + self.API_KEY
        ).read()
        response = json.loads(jsonResult)
        if not response["results"]:
            print("Address {} can not be geocoded! Check it.".format(address))
            return None
        return "place_id:" + response["results"][0]["place_id"]

    def __build_coords_str(self, coords):
        return ",".join([str(coord) for coord in coords])

    def __add_to_str(self, data, global_str):
        if (
            isinstance(data, list)
            and isinstance(data[0], (float, int))
            and isinstance(data[1], (float, int))
        ):
            global_str += self.__build_coords_str(data)
        elif isinstance(data, str):
            resp = self.__build_address_str(data)
            if resp is None:
                return None
            global_str += resp
        else:
            print("Address {} can not be geocoded! Check it.".format(data))
            return None
        return global_str

    def __adapt_addresses(self, addresses):
        for i in range(len(addresses)):
            if isinstance(addresses[i], str):
                addresses[i] = unidecode(addresses[i])

    def __check_status(self, response, origin, dest):
        possible_status = {
            "OK": "Valid result",
            "NOT_FOUND": "The origin and/or destination can not be geocoded.",
            "ZERO_RESULTS": "No route could be found between the origin and destination.",
            "MAX_ROUTE_LENGTH_EXCEEDED": "The requested route is too long and cannot be processed.",
        }
        global_check = True
        for i, row in enumerate(response["rows"]):
            for j, element in enumerate(row["elements"]):
                if element["status"] != "OK":
                    print(
                        possible_status[element["status"]]
                        + " Check directions {} and {}. One or both could be causing problems.".format(
                            origin[i], dest[j]
                        )
                    )
                    global_check = False
        return global_check

    def __call__(self, origin_dirs, dest_dirs):
        self.org_str = ""
        self.dst_str = ""
        self.__adapt_addresses(origin_dirs)
        self.__adapt_addresses(dest_dirs)
        # Create origin dirs
        for org in origin_dirs[:-1]:
            value = self.__add_to_str(org, self.org_str)
            if value is None:
                return None
            self.org_str = value + "|"
        value = self.__add_to_str(origin_dirs[-1], self.org_str)
        if value is None:
            return None
        self.org_str = value
        # Create destiny dirs
        for dst in dest_dirs[:-1]:
            value = self.__add_to_str(dst, self.dst_str)
            if value is None:
                return None
            self.dst_str = value + "|"
        value = self.__add_to_str(dest_dirs[-1], self.dst_str)
        if value is None:
            return None
        self.dst_str = value
        request = (
            self.DISTANCE_MATRIX_API_URL
            + "&origins="
            + self.org_str
            + "&destinations="
            + self.dst_str
            + "&key="
            + self.API_KEY
            + "&mode="
            + self.mode
        )
        jsonResult = urllib.request.urlopen(request).read()
        response = json.loads(jsonResult)
        if self.__check_status(response, origin_dirs, dest_dirs):
            return response
        else:
            return None
