import cPickle as pickle
import yaml

class PickleStorage:
    def __init__(self):
        self.data = {}
        pass

    def save(self, name, what):
        self.data[name] = what

    def load(self, name, default = None):
        try:
            return self.data[name]
        except KeyError:
            return default

    def connect(self):
        try:
            with open('state/world.pkl', 'r') as file:
                self.data = pickle.load(file)
            if self.data is None:
                self.data = {}
        except IOError:
            self.data = {}

    def commit(self):
        with open('state/world.pkl', 'w') as file:
            pickle.dump(self.data, file)

class YAMLStorage:
    def __init__(self):
        self.data = {}
        pass

    def save(self, name, what):
        self.data[name] = what

    def load(self, name, default = None):
        try:
            return self.data[name]
        except KeyError:
            return default

    def connect(self):
        try:
            with open('state/world.yaml', 'r') as file:
                self.data = yaml.load(file)
            if self.data is None:
                self.data = {}
        except IOError:
            self.data = {}

    def commit(self):
        with open('state/world.yaml', 'w') as file:
            yaml.dump(self.data, file)
