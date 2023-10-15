from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from utils.auxiliary import measure_execution_time


@measure_execution_time
def find_routes(problem_data, routing_data):
    """
    Find routes using a given problem data and routing data.

    This function takes in problem data and routing data and uses them to find routes using the Google OR-Tools library.

    Args:
        problem_data (dict): A dictionary containing the problem data, including the distance matrix, number of vehicles, start nodes, end nodes, max flight time, and velocity.
        routing_data (dict): A dictionary containing the routing data, including the first solution strategy, local search strategy, solution limit, time limit, log search flag, and LNS time limit.

    Returns:
        tuple: A tuple containing the problem data, routing index manager, routing model, and the solution to the routing problem.
    """
    for i in range(len(problem_data["distance_matrix"])):
        for j in range(len(problem_data["distance_matrix"][i])):
            problem_data["distance_matrix"][i][j] = int(
                problem_data["distance_matrix"][i][j]
            )

    # Create the routing index manager
    manager = pywrapcp.RoutingIndexManager(
        len(problem_data["distance_matrix"]),
        problem_data["n_vehicles"],
        problem_data["start_nodes"],
        problem_data["end_nodes"],
    )
    # Create Routing Model
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback
    def distance_callback(from_index, to_index):
        """
        Returns the distance between the two nodes
        """
        # Convert from routing variable Index to distance matrix NodeIndex
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return problem_data["distance_matrix"][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Distance constraint
    dimension_name = "Distance"
    routing.AddDimensionWithVehicleCapacity(
        transit_callback_index,
        0,  # no slack
        [
            int(16.6666666667 * v * t)
            for t, v in zip(problem_data["max_flight_time"], problem_data["velocity"])
        ],  # vehicle maximum travel time
        True,  # start cumul to zero
        dimension_name,
    )
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(
        max(problem_data["max_flight_time"]) * 60
    )

    # Setting first solution heuristic
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    strategy_value = getattr(
        routing_enums_pb2.FirstSolutionStrategy, routing_data["first_solution_strategy"]
    )
    search_parameters.first_solution_strategy = strategy_value

    # Setting search strategy
    strategy_value = getattr(
        routing_enums_pb2.LocalSearchMetaheuristic,
        routing_data["local_search_strategy"],
    )
    search_parameters.local_search_metaheuristic = strategy_value

    # Additional options to the routing problem
    if routing_data["solution_limit"] is not None:
        search_parameters.solution_limit = routing_data["solution_limit"]
    if routing_data["time_limit"] is not None:
        search_parameters.time_limit.seconds = routing_data["time_limit"]
    if routing_data["log_search"] is not None:
        search_parameters.log_search = routing_data["log_search"]
    if routing_data["lns_time_limit"] is not None:
        search_parameters.lns_time_limit.seconds = routing_data["lns_time_limit"]

    # Solve the problem and return the solution
    return (
        problem_data,
        manager,
        routing,
        routing.SolveWithParameters(search_parameters),
    )
