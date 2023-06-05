import random
import matplotlib.pyplot as plt
import numpy as np
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from utils import load_yaml


def generate_random_map(area_dims, n_points, depot_coords = [0,0,0], max_inspecting_time = 300):
    """ 
    Generates a random map, generating n_points in a area of dimensions area_dims[0]*area_dims[1] m^2
    """
    points = []
    points.append(depot_coords)
    while len(points) < n_points:
        x = random.randint(- area_dims[0] / 2, area_dims[0] / 2 - 1)
        y = random.randint(- area_dims[1] / 2, area_dims[1] / 2 - 1)
        insp_time = random.randint(0, max_inspecting_time)
        points.append([x, y, insp_time])
    return np.array(points)

def generate_distance_matrix(points, vel):
    """
    Create the time matrix between nodes (considering also the waiting time a each node)
    """
    num_points = len(points)
    distances = np.zeros((num_points, num_points), dtype = int)
    for i in range(num_points):
        for j in range(i+1, num_points):
            distance = np.linalg.norm(points[i,:2] - points[j,:2])
            distances[i, j] = int(distance / vel + points[j,2])
            distances[j, i] = int(distance / vel + points[i,2])
    return distances.tolist()

def plot_routes(points, routes):
    """
    Plot the map and routes for each vehicle
    """
    plt.scatter(points[:,0], points[:,1], color='blue', label='Nodes')
    plt.scatter(points[0,0], points[0,1], color='red', label='Depot')
    for route in routes:
        plt.plot(points[route,0], points[route,1], linestyle='dotted')
    plt.plot()
    for point in points:
        x = point[0]
        y = point[1]
        plt.text(x + 15, y + 15, str(point[2]), fontsize=10, verticalalignment='center', horizontalalignment='center')
    plt.xlabel('X [m]')
    plt.ylabel('Y [m]')
    plt.title('Generated Routes')
    plt.legend()
    plt.grid(True)
    plt.show()

def define_problem():
    """
    Stores the data for the problem
    """
    data = load_yaml("cfg/parameters.yaml")
    if data["nodes"] is None:
        data["nodes"] = generate_random_map(data["area_dims"], data["n_points"], depot_coords = [0,0,0], max_inspecting_time = data["max_flight_time"])
        data["distance_matrix"] = generate_distance_matrix(data["nodes"], data["velocity"])
    else:
        data["distance_matrix"] = generate_distance_matrix(data["nodes"], data["velocity"])
    return data


def print_solution(data, manager, routing, solution):
    """
    Prints solution on console
    """
    print(f'Objective: {solution.ObjectiveValue()}')
    max_route_time = 0
    routes = []
    for vehicle_id in range(data['n_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_time = 0
        nodes = []
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            nodes.append(node)
            plan_output += ' {} -> '.format(node)
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_time += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        node = manager.IndexToNode(index)
        nodes.append(node)
        route_mins = route_time // 60
        route_secs = route_time % 60
        plan_output += '{}\n'.format(manager.IndexToNode(index))
        plan_output += 'Time to complete the route: {}min {}secs\n'.format(route_mins, route_secs)
        print(plan_output)
        max_route_time = max(route_time, max_route_time)
        routes.append(nodes)
    max_route_mins = max_route_time // 60
    max_route_secs = max_route_time % 60
    print('Time to complete the longest route: {}min {}secs\n'.format(max_route_mins, max_route_secs))
    plot_routes(data["nodes"], routes)



def main():
    # Instantiate the data problem
    data = define_problem()

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['n_vehicles'], 0)
    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback.
    def distance_callback(from_index, to_index):
        """
        Returns the distance between the two nodes
        """
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Distance constraint.
    dimension_name = 'Distance'
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        data["max_flight_time"] * 60,  # vehicle maximum travel time
        True,  # start cumul to zero
        dimension_name)
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        print_solution(data, manager, routing, solution)
    else:
        print('No solution found !')


if __name__ == '__main__':
    # points = generate_random_map(area_dims=(1000,2000), n_points=30)
    # plot_routes(points)
    # distances = generate_distance_matrix(points,3)
    # print(distances)
    main()