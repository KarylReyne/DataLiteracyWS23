"""?DEPRECATED?"""
import os
import json

default_path = f".{os.sep}src{os.sep}config{os.sep}"
masterconfigfile = "config.json"


def write_config(config, path=default_path, file=masterconfigfile):
    with open(path + file, 'w') as configfile:
        json.dump(config, configfile, indent=4)
        configfile.close()


def edit_config(config_dict, path=default_path, file=masterconfigfile):
    with open(path + file, 'r') as configfile:
        config = json.load(configfile)
        for key in config_dict:
            config[key] = config_dict[key]
        configfile.close()
    write_config(config, default_path, masterconfigfile)


def get_config(key, path=default_path, file=masterconfigfile):
    with open(path + file, 'r') as configfile:
        config = json.load(configfile)
        try:
            value = config[key]
        except KeyError:
            raise InvalidConfigKey(key, file)
    return value


class InvalidConfigKey(Exception):
    """The given key is not in the config file."""

    def __init__(self, key, file=masterconfigfile, *args: object) -> None:
        message = f"The given key '{key}' is not in the given config file '{file}'."
        super().__init__(message, *args)