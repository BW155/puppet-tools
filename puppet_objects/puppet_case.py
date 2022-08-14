class PuppetCase:
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
        return '<PuppetCase: %s>' % self.name
