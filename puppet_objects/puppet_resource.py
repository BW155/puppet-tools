
class PuppetResource:
    def __init__(self, typ):
        self.typ = typ
        self.name = ""
        self.items = []

    def add_item(self, item):
        self.items.append(item)

    def print_items(self, depth=0):
        for i in self.items:
            print("\t" * depth, i)

    def __repr__(self):
        return '<PuppetResource \'%s\': \'%s\'>' % (self.typ, self.name)
