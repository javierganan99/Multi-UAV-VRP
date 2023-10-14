from utils.auxiliary import load_yaml
from pathlib import Path
import os


def load_problem_definiton(
    file=str(
        Path(__file__).parent.resolve()
        / os.path.sep.join(["..", "cfg", "problem_definition.yaml"])
    ),
):
    """
    Loads the definition for the problem
    """
    return load_yaml(file)


def load_solver_configuration(
    file=str(
        Path(__file__).parent.resolve()
        / os.path.sep.join(["..", "cfg", "solver_configuration.yaml"])
    )
):
    """
    Loads the configuration for the solver
    """
    return load_yaml(file)
