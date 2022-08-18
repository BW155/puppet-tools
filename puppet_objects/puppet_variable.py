from puppet_objects import PuppetObject


class PuppetVariable(PuppetObject):
    def __init__(self, name):
        self.name = name
        self.items = []
        self.value = None

    def add_item(self, item):
        pass

    def print_items(self, depth=0):
        print(self)

    def __repr__(self):
        return "<PuppetVariable: '%s' = %s>" % (self.name, self.value)
