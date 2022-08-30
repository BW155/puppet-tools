from abc import abstractmethod


class PuppetObject:
    items = []

    @abstractmethod
    def print_items(self, depth=0):
        pass


# from .puppet_block import PuppetBlock
# from .puppet_file import PuppetFile
# from .puppet_case import PuppetCase
# from .puppet_case_item import PuppetCaseItem
# from .puppet_include import PuppetInclude
# from .puppet_resource import PuppetResource
# from .puppet_variable import PuppetVariable
