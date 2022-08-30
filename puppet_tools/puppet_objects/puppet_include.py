from . import PuppetObject


class PuppetInclude(PuppetObject):
    def __init__(self, name):
        self.name = name

    def print_items(self, depth=0):
        pass

    def __repr__(self):
        return '<PuppetInclude: %s>' % self.name
