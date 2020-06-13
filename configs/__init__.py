from . import default_configs
import importlib

class Configs(object):
    def __init__(self, module):
        self.attributes = {}
        self.set_module(default_configs)
        self.set_module(module)

    def __getitem__(self, item):
        return self.get(item)

    def set_module(self, module):
        if isinstance(module, (str, unicode)):
            module = importlib.import_module(module)
        for key in dir(module):
            if str.isupper(key):
                self.set(key, getattr(module, key))

    def set(self, key, value):
        self.attributes[key] = value

    def get(self, key):
        if key not in self.attributes:
            return None
        return self.attributes[key]


