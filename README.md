# Multi-UAV Vehicle Routing Problem

This repository provides an Human-Machine Interface (HMI) to solve the Vehicle Routing Problem (VRP) for a heterogeneous swarm of Unmanned Aerial Vehicles (UAVs). It optimizes the time in which **N** UAVs visit **M** locations, considering the diverse capabilities of each vehicle and adhering to each drone's restrictions.

## 📋 Features

- [x] **Multi-depot**: Define several departure and arrival depots. Each UAV can take off and land at different locations.

- [x] **Heterogeneity**: Each vehicle can possess distinct capabilities, including various velocities and battery requirements (maximum time of flight).

- [x] **HMI**: Interact with the web application to define the problem interactively. Add addresses or coordinates to visit, and specify each vehicle's capabilities. Generate, simulate, and save the routes and the problem definition. Configuration files are also supported.

- [x] **Simulation**: Simulate the route generation and real-time execution of UAVs.

- [x] [**OR-Tools**](https://developers.google.com/optimization): Currently leveraging the [OR-Tools open-source library for combinatorial optimization](https://github.com/google/or-tools) to compute the routes. Other methods can be seamlessly integrated (see [Routes Computation](#🗺️-routes-computation) section).

- [ ] **Replanning**: Routes recomputation when the original problem definition changes (vehicle lost, new vehicle addition, etc). 

## ⚙️ Installation

1. To install Multi-UAV-VRP you can create a conda environment (optional).

```ssh
conda create --name vrp
conda activate vrp
```

2. Clone the repository.

```ssh
git clone https://github.com/javierganan99/Multi-UAV-VRP.git
cd Multi-UAV-VRP
```

3. Install the requirements.

```ssh
pip install -r requirements.txt
```

## 🖥️ Usage

To use the HMI, you need a [Google Maps API Key](https://developers.google.com/maps/documentation/javascript/get-api-key) to load the map into the webpage. 

1. Set your Google Maps API Key as an enviroment variable.
    
Linux and Mac:
```ssh
export MAPS_API_KEY=<YOUR_API_KEY>
```

Windows:
```
setx MAPS_API_KEY <YOUR_API_KEY>
```
2. Launch the web app.

```
python3 /path/to/Multi-UAV-VRP/main.py
```

## ✍🏼 Problem Definition

You can define the problem using configuration files, the HMI, or a hybrid approach.

The default problem definiton is located at **/path/to/Multi-UAV-VRP/cfg/problem_definition.yaml** file. You can load it to the HMI using the **Load Problem Definition from File** button.

Within the HMI, you can overwrite the following problem elements: 
    
- **Number of vehicles**: The **N** number of UAVs.
- **Maximun time-of-fligh per vehicle**: A list of **N** times in the format *t1, t2, ..., tn*.
- **Velocity of each vehicle**: A list of **N** velocities in the format *v1, v2, ..., vn*.
- **Departure depots**: Introduce the **N** departure locations' indexes in a list *i1, i2, ..., in*.
- **Arrival depots**: The same as **Departure depots** but for the arrival depots of the drones.

You can also add or delete the locations to visit. Use the **Directions** text box or click the position on the map to add a direction. The **Directions** text box accepts human-readable directions (e.g., *La giralda, Seville*), and *latitude, longitude* coordinates (e.g., *37.411872181, -6.001852909*). To delete locations, hover over the map location marker and click *Delete*.

The *Travel mode* can be selected in the HMI, supporting the following modes: *Flight, Driving, Walking, Biking, and Transit*. Except for *Flight*, all modes compute the distance between each location using the [Distace Matrix Google API](https://developers.google.com/maps/documentation/distance-matrix). In the *flight* mode, the [Haversine formula](https://en.wikipedia.org/wiki/Haversine_formula) is employed without using any external API.

> Note that although UAVs often fly without restrictions between 2 locations, certain applications such as surveillance or monitoring might require the drones to follow specific paths, like roads, bike paths, or pedestrian paths. For such cases, the travel distance is estimated more precisely using suitable travel modes.

> ⚠️ If you use a *Travel mode* other than the *Flight* mode and your problem includes more than ~50 locations, be cautious. Calculating the **Distance Matrix** might take too long for time-critical applications. Additionally, excessive use of the HMI (specially in modes other than *Flight*) may incur costs due to exceeding the free [Distace Matrix Google API](https://developers.google.com/maps/documentation/distance-matrix) requests.

## 🗺️ Routes Computation

We currently support [OR-Tools open-source Python library](https://github.com/google/or-tools) for routes calculation. It is [well-documented](https://developers.google.com/optimization/reference/python/index_python) and provides [useful utilities for routing problems](https://developers.google.com/optimization/reference/python/constraint_solver/pywrapcp), such as the VRP. Refer to their [guide](https://developers.google.com/optimization/routing) for examples related to the VRP problem.

In this project, we define the `find_routes` function in the **/path/to/Multi-UAV-VRP/app/utils/or_tools_method.py** file to compute optimized routes. You can modify this function or create a new one to solve the VRP with other methods. Define your problem related parameters and your method's parameters in the **/path/to/Multi-UAV-VRP/cfg/problem_definition.yaml** and the **/path/to/Multi-UAV-VRP/cfg/solver_configuration.yaml** configuration files, respectively. Your function should take input from both dictionaries.

You can create another function to adapt the output format of the solution to be compatible with Multi-UAV VRP. We currently use `adapt_solution` function to convert the OR-Tools format to the required format.  This function should take the output of the `find_routes` function and produce a dictionary in the following format:
```python
result = {
    'routes': {
        # N vehicle IDs, should be integers from 0 to (N-1)
        0: {
             # Latitude and longitude list of nodes to visit
            'coordinates': [(37.3830519, -5.9902257), (37.3842311, -5.9709563), ...],
             # A list representing the indexes of the coordinates of the routes in the problem definition
            'nodes': [20, 10, 2, ...],
             # Estimated time to complete the route [s]
            'time': 12069,
            # Hexadecimal color to visualize the route path
            'color': '#00FF00',
            # Velocity of the vehicle [m/s]
            'velocity': 3.2, 
        }
        1: ...
    },
    # Time to complete the longest route [s]
    'total_time': 15000
}
```

## 📬 Contact

Francisco Javier Gañán - fjganan14@gmail.com
