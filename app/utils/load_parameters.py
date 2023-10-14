from app.utils.auxiliary import load_yaml


def load_problem_definiton(file="cfg/problem_definition.yaml"):
    """
    Loads the definition for the problem
    """
    return load_yaml(file)


def load_solver_configuration(file="cfg/solver_configuration.yaml"):
    """
    Loads the configuration for the solver
    """
    return load_yaml(file)
