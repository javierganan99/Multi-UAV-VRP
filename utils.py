import yaml
import os

def load_yaml(file):
    """
    This function loads a yaml file
    """
    assert os.path.exists(file), "File not found in path {}".format(file)
    with open(file, "r") as f:
        params = yaml.safe_load(f)
    return params