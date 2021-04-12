import configparser
import pkg_resources
import os


def get_config_value(group: str, key: str) -> str:
    config = configparser.ConfigParser()
    path = os.path.join(os.path.dirname(__file__), "resources", "config.ini")
    config.read(path)
    return config.get(group, key)
