from abc import abstractmethod


class PuppetObject:
    items = []

    @abstractmethod
    def print_items(self, depth=0):
        pass
