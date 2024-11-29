import os
from configparser import ConfigParser

def get_path():
    return os.path.dirname(os.path.abspath(__file__))

def get_config(path=None):
    config_path = path if path else get_path()

    config = ConfigParser()
    config.read(f"{config_path}/config/offset.ini")

    return config

def get_offset():
    config = get_config()

    return int(config["DEFAULT"]["offset"])

def set_offset(offset):
    config = get_config()
    config.set("DEFAULT", "offset", offset)

    with open(f"{path}/config/offset.ini", 'w') as configfile:
        config.write(configfile)