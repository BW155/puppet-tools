from puppet_objects import PuppetObject


class PuppetResource(PuppetObject):
    TYPES = ["package", "file", "service", "cron", "exec", "stage", "firewall"]

    META_PARAMETERS = ["alias", "audit", "before", "loglevel", "noop", "notify", "require", "schedule", "stage", "subscribe", "tag"]

    ALLOWED_RESOURCE_FILE_ITEMS = ["ensure", "path", "owner", "group", "mode", "source", "content", "recurse", "purge",
                                   "target", "backup", "checksum", "force", "ignore", "links", "recurselimit",
                                   "replace"] + META_PARAMETERS
    ALLOWED_RESOURCE_SERVICE_ITEMS = ["name", "ensure", "enable", "hasrestart", "hasstatus"] + META_PARAMETERS
    ALLOWED_RESOURCE_PACKAGE_ITEMS = ["name", "ensure", "source", "provider"] + META_PARAMETERS
    ALLOWED_RESOURCE_EXEC_ITEMS = ["command", "path", "returns", "environment", "creates", "refreshonly", "onlyif", "unless"] + META_PARAMETERS
    ALLOWED_RESOURCE_CRON_ITEMS = ["command", "special", "user", "hour", "minute", "ensure"] + META_PARAMETERS

    def __init__(self, typ):
        self.typ = typ
        self.is_dependency = False
        self.name = ""
        self.items = []

    def get_value_for_item_name(self, search_name):
        result = None
        for i in self.items:
            name, value = i.split("=>")
            if name.lstrip().rstrip() == search_name:
                result = value.lstrip().rstrip()

        return result

    def add_item(self, item: str):
        self.items.append(item)

    def print_items(self, depth=0):
        for i in self.items:
            print("\t" * depth, i)

    def set_dependency(self):
        self.is_dependency = True

    def __repr__(self):
        return '<PuppetResource \'%s\': \'%s\', dependency: %d>' % (self.typ, self.name, self.is_dependency)
