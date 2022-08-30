from . import PuppetObject


class PuppetVariable(PuppetObject):
    def __init__(self, name):
        self.name = name
        self.value = None

    def print_items(self, depth=0):
        print(self)

    def set_value(self, value):
        self.value = value

    def __repr__(self):
        return "<PuppetVariable: '%s' = %s>" % (self.name, self.value)
