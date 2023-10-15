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

    Args:
        file (str): The path to the YAML file containing the problem definition (default is the default YAML file path).

    Returns:
        dict: The loaded problem definition as a dictionary."""
    return load_yaml(file)


def load_solver_configuration(
    file=str(
        Path(__file__).parent.resolve()
        / os.path.sep.join(["..", "cfg", "solver_configuration.yaml"])
    )
):
    """
    Loads the configuration for the solver

    Args:
        file (str, optional): The file path of the configuration (default is the path to the solver_configuration.yaml file)

    Returns:
        dict: The loaded configuration as a dictionary"""
    return load_yaml(file)
