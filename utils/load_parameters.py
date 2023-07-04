from utils.auxiliary import load_yaml


def load_problem_definiton(file="cfg/problem_definition.yaml"):
    """
    Loads the definition for the problem
    """
    data = load_yaml(file)
    # if "distance_matrix" not in data.keys():
    #     from utils.problem_definiton import generate_distance_matrix

    #     data["distance_matrix"] = generate_distance_matrix(data["addresses"])
    return data


def load_solver_configuration(file="cfg/solver_configuration.yaml"):
    """
    Loads the configuration for the solver
    """
    data = load_yaml(file)
    return data


def load_iternal_parameters(file="cfg/internal.yaml"):
    """
    Load internal configuration for the project
    """
    data = load_yaml(file)
    return data