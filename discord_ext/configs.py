import traceback

import json5 as json

config_list_default = {"logger": "log_config.json5"}


def get_json(filename):
    return json.load(open(filename, encoding="UTF-8"), encoding="UTF-8")


class ConfigsManager:
    def __init__(self, configs_proxy):
        self.configs_proxy = configs_proxy

    @property
    def logger(self):
        return self.configs_proxy["logger"]


def init_configs(configs_proxy,
                 configs_list: dict = None,
                 ):
    configs_list = configs_list if configs_list is not None else config_list_default
    for name, file in config_list_default.items():
        try:
            configs_proxy[name] = json.load(open(file, encoding="UTF-8"), encoding="UTF-8")

        except FileExistsError:
            print("File not Found")
        except Exception as e:
            traceback.print_exception(e)

    print(configs_proxy)
