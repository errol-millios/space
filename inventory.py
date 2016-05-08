import yaml

class Item:
    def __init__(self, *kwargs):
        # kg
        self.mass = kwargs['mass'] if 'mass' in kwargs else 0

        # dm^3
        self.space = kwargs['space'] if 'space' in kwargs else 0
        self.value = kwargs['value'] if 'value' in kwargs else 0
        self.name = kwargs['name'] if 'name' in kwargs else 'A piece of junk'
        self.desc = kwargs['desc'] if 'desc' in kwargs else 'It looks useless.'

class Catalog:
    def __init__(self):
        self._items = None

    def items(self):
        if self._items is None:
            with open('resources/inventory.yaml', 'r') as file:
                self._items = yaml.load(file.read())
        return self._items

    def get(self, *keys):
        try:
            d = self.items()
            for key in keys:
                d = d[key]
            return d
        except KeyError:
            return None



if __name__ == '__main__':
    print Catalog().items()
    print Catalog().items()
