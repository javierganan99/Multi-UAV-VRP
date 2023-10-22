import json
import math
import urllib.request
from unidecode import unidecode
import numpy as np


def calculate_haversine_distance(c1, c2):
    """
    Calculate distance between 2 coordinates using haversine formula.

    Args:
        c1 (tuple): A tuple containing the latitude, longitude,
            and maybe alitude of the first coordinate.
        c2 (tuple): A tuple containing the latitude, longitude,
            and maybe alitude of the second coordinate.

    Returns:
        float: The distance between the two coordinates in meters."""
    if len(c1) == 3 and len(c2) == 3:
        lat1, lon1, alt1 = c1
        lat2, lon2, alt2 = c2
    else:
        lat1, lon1 = c1[:2]
        lat2, lon2 = c2[:2]
        alt1, alt2 = None, None

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
    if alt1 and alt2:
        return math.sqrt((radius * c) ** 2 + (alt2 - alt1) ** 2)
    return radius * c


def generate_flight_distance_matrix(coordinates):
    """
    Create distance matrix using haversine formula

    Args:
        coordinates (list): List of coordinate tuples (latitude, longitude).

    Returns:
        list: Distance matrix where each element represents the distance between two coordinates.
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
    api_key,
    geocode_api_url,
    distance_matrix_api_url,
    mode="walking",
    max_elements=10,
):
    """
    Generate a distance matrix of the specified addresses.

    Args:
        addresses (list): List of addresses to generate the distance matrix.
        api_key (str): API key for accessing the Distance Matrix API.
        geocode_api_url (str): URL for the Geocode API.
        distance_matrix_api_url (str): URL for the Distance Matrix API.
        mode (str, optional): Mode of transport for the distance request (default is "walking").
        max_elements (int, optional): Maximum number of elements in each request (default is 10).

    Returns:
        list: The distance matrix as a list of lists."""
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
        api_key=api_key,
        geocode_api_url=geocode_api_url,
        distance_matrix_api_url=distance_matrix_api_url,
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
                raise RuntimeError("The distance matrix could not be calculated!")
            submatrix = build_distance_matrix(response)
            distance_matrix = fill_matrix(ind_row, ind_col, distance_matrix, submatrix)
            ind_col += len(submatrix[0])
        ind_row += len(submatrix)
    distance_matrix = distance_matrix.astype(int)
    return distance_matrix.tolist()


def detect_address_format(address: str):
    """
    Detects the format of an address based on its structure.

    This function takes an address as input and determines its format based
    on the structure of the address. It can detect addresses in three
    different formats: float-coordinates, str-coordinates, and name.

    Args:
        address (str): The address to be analyzed.

    Returns:
        str: The format of the address. It can be "float-coordinates", "str-coordinates" or "name".
    """
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
    return "name"


class AddressFormatConversion:
    """
    Converts the given address from the input format to the corresponding coordinates.

    Args:
        api_key (str): The API key required to access the geocoding and distance matrix services.
        geocode_api_url (str): The URL of the geocoding API.
        DISTANCE_MATRIX_API_URL (str): The URL of the distance matrix API.

    Attributes:
        api_key (str): The API key required to access the geocoding and distance matrix services.
        geocode_api_url (str): The URL of the geocoding API.
        distance_matrix_api_url (str): The URL of the distance matrix API.

    Methods:
        __init__(api_key, geocode_api_url, distance_matrix_api_url): Initializes the
            AddressFormatConversion object with the provided API key and API URLs.
        address2coords(address): Given an address in str format, return its coordinates.
    """

    def __init__(self, api_key, geocode_api_url, distance_matrix_api_url):
        """
        Initializes the API key and API URLs for the class.

        Args:
            api_key (str): The API key for accessing the APIs.
            geocode_api_url (str): The URL for the geocode API.
            distance_matrix_api_url (str): The URL for the distance matrix API.

        Returns:
            None"""
        self.api_key, self.geocode_api_url, self.distance_matrix_api_url = (
            api_key,
            geocode_api_url,
            distance_matrix_api_url,
        )

    def address2coords(self, address):
        """
        Given an address in str format, return its coordinates

        Args:
            address (str): The address to geocode.

        Returns:
            list: The coordinates of the address in the format [latitude, longitude]."""
        address = unidecode(address)
        json_result = urllib.request.urlopen(
            self.geocode_api_url
            + "address="
            + address.replace(" ", "+")
            + "&key="
            + self.api_key
        ).read()
        response = json.loads(json_result)
        if not response["results"]:
            print(f"Address {address} can not be geocoded! Check it.")
            return None
        return [
            float(response["results"][0]["geometry"]["location"]["lat"]),
            float(response["results"][0]["geometry"]["location"]["lng"]),
        ]


class DistanceMatrixRequest:
    """
    This class represents a request to the Distance Matrix API and provides
    functionality for building the request URL,
    handling addresses and coordinates, and checking the status of the response.

    Args:
        api_key (str): The API key for the distance calculator service.
        geocode_api_url (str): The URL for the geocode API.
        distance_matrix_api_url (str): The URL for the distance matrix API.
        mode (str, optional): The transportation mode for distance requests.
            Must be one of "driving", "walking", "bicycling", or "transit". Defaults to "DRIVING".

    Attributes:
        api_key (str): The API key for the distance calculator service.
        geocode_api_url (str): The URL for the geocode API.
        distance_matrix_api_url (str): The URL for the distance matrix API.
        mode (str): The transportation mode for distance requests.
        available_modes (list): The list of available transportation modes.

    Methods:
        __init__(api_key, geocode_api_url, distance_matrix_api_url, mode):
            Constructor for the DistanceMatrixRequest class.
        __call__(origin_dirs, dest_dirs): Performs the distance matrix request.

    Private Methods:
        __build_address_str(address): Builds a string representation
            of the Google Maps geocoding API request URL for a given address.
        __build_coords_str(coords): Builds a string representation of coordinates.
        __add_to_str(data, global_str): Adds data to a global string.
        __adapt_addresses(addresses): Adapts addresses by replacing any accented
            characters with their unaccented counterparts.
        __check_status(response, origin, dest): Checks the status of a geocoding
            response and prints any errors encountered.
    """

    def __init__(
        self, api_key, geocode_api_url, distance_matrix_api_url, mode="DRIVING"
    ):
        """
        This function initializes a DistanceCalculator object with the provided API key,
        geocode API URL, distance matrix API URL, and mode of transportation (default is "DRIVING").

        Args:
            api_key (str): The API key for the distance calculator service.
            geocode_api_url (str): The URL for the geocode API.
            distance_matrix_api_url (str): The URL for the distance matrix API.
            mode (str, optional): The transportation mode for distance requests.
                Must be one of "driving", "walking", "bicycling", or "transit".
                Defaults to "DRIVING".

        Returns:
            None"""
        self.api_key, self.geocode_api_url, self.distance_matrix_api_url = (
            api_key,
            geocode_api_url,
            distance_matrix_api_url,
        )
        self.mode = mode
        self.available_modes = ["driving", "walking", "bicycling", "transit"]
        assert mode in self.available_modes, "Distance request mode not available!"

    def __build_address_str(self, address):
        """
        Builds a string representation of the Google Maps
        geocoding API request URL for a given address.

        Args:
            self (object): The instance of the class that the method is called on.
            address (str): The address to geocode.

        Returns:
            str: A string containing the place_id of the first result from the
                geocoding API response, or None if no results were found.
        """
        json_result = urllib.request.urlopen(
            self.geocode_api_url
            + "address="
            + address.replace(" ", "+")
            + "&key="
            + self.api_key
        ).read()
        response = json.loads(json_result)
        if not response["results"]:
            print(f"Address {address} can not be geocoded! Check it.")
            return None
        return "place_id:" + response["results"][0]["place_id"]

    def __build_coords_str(self, coords):
        """
        Builds a string representation of coordinates.

        This function takes a list of coordinates and builds a string representation
        of them by joining each coordinate with a comma.

        Args:
            coords (list): The list of coordinates to be converted into a string representation.

        Returns:
            str: The string representation of the coordinates."""
        return ",".join([str(coord) for coord in coords])

    def __add_to_str(self, data, global_str):
        """
        Adds data to a global string.

        This function checks the type of the data and adds it to the global string accordingly.
        If the data is a list of floats or integers, the coordinates string
        is built and added to the global string.
        If the data is a string, the address string is built and added to the global string.
        If the data is neither a list of floats or integers nor a string,
        an error message is printed and None is returned.

        Args:
            data (list or str): The data to be added to the global string.
            global_str (str): The global string to which the data will be added.

        Returns:
            str or None: The updated global string if data was added successfully,
                or None if an error occurred.
        """
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
            print(f"Address {data} can not be geocoded! Check it.")
            return None
        return global_str

    def __adapt_addresses(self, addresses):
        """
        This function adapts addresses by replacing any accented
        characters with their unaccented counterparts.

        Args:
            addresses (list): A list of addresses to adapt.

        Returns:
            None"""
        for i, address in enumerate(addresses):
            if isinstance(address, str):
                addresses[i] = unidecode(address)

    def __check_status(self, response, origin, dest):
        """
        Checks the status of a geocoding response and prints any errors encountered.

        This function takes a geocoding response, origin addresses, and destination addresses.
        It checks the status of each element in the response and prints an error message for
        any element with a status other than "OK". The function returns a boolean indicating
        whether all elements in the response have a status of "OK".

        Args:
            response (dict): The geocoding response containing "rows" and "elements" data.
            origin (list): The list of origin addresses.
            dest (list): The list of destination addresses.

        Returns:
            bool: True if all elements in the response have a status of "OK", False otherwise.
        """
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
                        f"{possible_status[element['status']]} Check directions {origin[i]} and \
                            {dest[j]}. One or both could be causing problems."
                    )
                    global_check = False
        return global_check

    def __call__(self, origin_dirs, dest_dirs):
        """
        Calls the Google Distance Matrix API to retrieve the distance
        and duration between origin and destination addresses.

        Args:
            origin_dirs (list): A list of origin addresses.
            dest_dirs (list): A list of destination addresses.

        Returns:
            dict: A dictionary containing the response from the API,
                including distance and duration information.
        """
        org_str = ""
        dst_str = ""
        self.__adapt_addresses(origin_dirs)
        self.__adapt_addresses(dest_dirs)
        # Create origin dirs
        for org in origin_dirs[:-1]:
            value = self.__add_to_str(org, org_str)
            if value is None:
                return None
            org_str = value + "|"
        value = self.__add_to_str(origin_dirs[-1], org_str)
        if value is None:
            return None
        org_str = value
        # Create destiny dirs
        for dst in dest_dirs[:-1]:
            value = self.__add_to_str(dst, dst_str)
            if value is None:
                return None
            dst_str = value + "|"
        value = self.__add_to_str(dest_dirs[-1], dst_str)
        if value is None:
            return None
        dst_str = value
        request = (
            self.distance_matrix_api_url
            + "&origins="
            + org_str
            + "&destinations="
            + dst_str
            + "&key="
            + self.api_key
            + "&mode="
            + self.mode
        )
        json_result = urllib.request.urlopen(request).read()
        response = json.loads(json_result)
        if self.__check_status(response, origin_dirs, dest_dirs):
            return response
        return None
