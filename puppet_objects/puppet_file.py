from constants import SPLIT_TOKEN
from puppet_objects import PuppetObject


class PuppetFile(PuppetObject):
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
