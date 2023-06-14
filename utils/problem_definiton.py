import json
import urllib.request
from unidecode import unidecode
from utils.load_parameters import load_iternal_parameters


def generate_distance_matrix(addresses, mode="walking"):
    """
    Generate a distance matrix of the specified addresses.
    """
    available_modes = ["driving", "walking", "bycycling", "transit", "flight"]
    assert mode in available_modes, "Distance request mode not available!"

    def build_distance_matrix(response):
        distance_matrix = []
        for row in response["rows"]:
            row_list = [row["elements"][j]["distance"]["value"] for j in range(len(row["elements"]))]
            distance_matrix.append(row_list)
        return distance_matrix

    send_request = DistanceMatrixRequest(mode=mode)  # To perform request to Distance Matrix API
    max_elements = 100  # Max elements accepted by Distance Matrix API
    num_addresses = len(addresses)
    max_rows = max_elements // num_addresses
    q, r = divmod(num_addresses, max_rows)
    dest_addresses = addresses
    distance_matrix = []
    rest = 1 if r > 0 else 0
    for i in range(q + rest):
        origin_addresses = addresses[i * max_rows : (i + 1) * max_rows]
        response = send_request(origin_addresses, dest_addresses)
        if response is None:
            raise Exception("The distance matrix could not be calculated!")
        distance_matrix += build_distance_matrix(response)
    print(print("\n".join(["\t".join([str(cell) for cell in row]) for row in distance_matrix])))
    return distance_matrix


def detect_address_format(address: str):
    if isinstance(address, list) and isinstance(address[0], (float, int)) and isinstance(address[1], (float, int)):
        return "float-coordinates"
    address = address.replace(" ", "").split(",")
    if isinstance(address, list) and isinstance(address[0], (float, int)) and isinstance(address[1], (float, int)):
        return "str-coordinates"
    else:
        return "name"


class AddressFormatConversion:
    def __init__(self):
        data = load_iternal_parameters()
        self.API_KEY, self.GEOCODE_API_URL, self.DISTANCE_MATRIX_API_URL = (
            data["API_KEY"],
            data["GEOCODE_API_URL"],
            data["DISTANCE_MATRIX_API_URL"],
        )

    def address2coords(self, address):
        """
        Given an address in str format, return its coordinates
        """
        address = unidecode(address)
        jsonResult = urllib.request.urlopen(
            self.GEOCODE_API_URL + "address=" + address.replace(" ", "+") + "&key=" + self.API_KEY
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

    def __init__(self, mode="DRIVING"):
        data = load_iternal_parameters()
        self.API_KEY, self.GEOCODE_API_URL, self.DISTANCE_MATRIX_API_URL = (
            data["API_KEY"],
            data["GEOCODE_API_URL"],
            data["DISTANCE_MATRIX_API_URL"],
        )
        self.mode = mode
        self.available_modes = ["driving", "walking", "bycycling", "transit"]
        assert mode in self.available_modes, "Distance request mode not available!"

    def __build_address_str(self, address):
        jsonResult = urllib.request.urlopen(
            self.GEOCODE_API_URL + "address=" + address.replace(" ", "+") + "&key=" + self.API_KEY
        ).read()
        response = json.loads(jsonResult)
        if not response["results"]:
            print("Address {} can not be geocoded! Check it.".format(address))
            return None
        return "place_id:" + response["results"][0]["place_id"]

    def __build_coords_str(self, coords):
        return ",".join([str(coord) for coord in coords])

    def __add_to_str(self, data, global_str):
        if isinstance(data, list) and isinstance(data[0], (float, int)) and isinstance(data[1], (float, int)):
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
        for org, dst in zip(origin_dirs[:-1], dest_dirs[:-1]):
            value = self.__add_to_str(org, self.org_str)
            if value is None:
                return None
            self.org_str = value + "|"
            value = self.__add_to_str(dst, self.dst_str)
            if value is None:
                return None
            self.dst_str = value + "|"
        value = self.__add_to_str(origin_dirs[-1], self.org_str)
        if value is None:
            return None
        self.org_str = value
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
