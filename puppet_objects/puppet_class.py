from constants import SPLIT_TOKEN


class PuppetClass:
    def __init__(self, name):
        self.name = name
        self.items = []

    def add_item(self, item):
        self.items.append(item)

    def print_items(self, depth=0):
        for i in self.items:
            print("\t" * depth, i)
            i.print_items(depth + 1)

    def __repr__(self):
        return '<PuppetClass: %s>' % self.name


class PuppetFile:
    def __init__(self, path):
        self.name = path.split(SPLIT_TOKEN)[-1]
        self.path = path
        self.items = []

    def add_item(self, item):
        self.items.append(item)

    def print_items(self):
        for i in self.items:
            print(i)
            i.print_items()

    def __repr__(self):
        return '<PuppetFile: %s, items: ' % self.name + ', '.join([str(i) for i in self.items]) + ">"
