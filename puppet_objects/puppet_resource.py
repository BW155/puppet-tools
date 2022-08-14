
class PuppetResource:
    def __init__(self, typ):
        self.typ = typ
        self.is_dependency = False
        self.name = ""
        self.items = []

    def add_item(self, item):
        self.items.append(item)

    def print_items(self, depth=0):
        for i in self.items:
            print("\t" * depth, i)

    def set_dependency(self):
        self.is_dependency = True

    def __repr__(self):
        return '<PuppetResource \'%s\': \'%s\', dependency: %d>' % (self.typ, self.name, self.is_dependency)
