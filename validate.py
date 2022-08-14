import os

from constants import LOG_TYPE_ERROR, SPLIT_TOKEN, LOG_TYPE_FATAL
from puppet_objects import PuppetObject
from puppet_objects.puppet_case import PuppetCase
from puppet_objects.puppet_case_item import PuppetCaseItem
from puppet_objects.puppet_class import PuppetClass
from puppet_objects.puppet_include import PuppetInclude
from puppet_objects.puppet_resource import PuppetResource
from utility import add_log


def sort_puppet_objects(puppet_object, results=None, index_list=None):
    if index_list is None:
        index_list = []
    if results is None:
        results = {}

    if isinstance(puppet_object, PuppetObject):
        if puppet_object.items:
            for i, it in enumerate(puppet_object.items):
                index_list.append(i)
                if type(it) not in results:
                    results[type(it)] = []
                results[type(it)].append((index_list, it))
                results = sort_puppet_objects(it, results, index_list)
    return results


def find_base_class(classes):
    for i, c in enumerate(classes):
        if "::" not in c.name:
            return i, c


def process_puppet_module(puppet_files, module_name, module_dir):
    file_results = [sort_puppet_objects(f) for f in puppet_files]

    def get_type(t):
        return [r[1] for result in file_results if t in result for r in result[t]]

    def get_resource_type(t):
        return [r for r in get_type(PuppetResource) if r.typ == t]

    classes = get_type(PuppetClass)
    includes = get_type(PuppetInclude)
    case_items = get_type(PuppetCaseItem)
    packages = get_resource_type("package")
    services = get_resource_type("service")
    cron = get_resource_type("cron")
    files = get_resource_type("file")
    execs = get_resource_type("exec")

    if not all([module_name in cl.name for cl in classes]):
        add_log(module_name, LOG_TYPE_FATAL, (0, 0),
                "Please check the provided module name and/or classes, the module name should be in the class names, "
                "found: '%s'" % module_name, "")
        return

    # Summary
    print("")
    print("Module '%s' Content Summary:" % module_name)
    print("Classes:\t", ", ".join(list(set(c.name for c in classes))))
    print("Case items:\t", ", ".join(list(set(c.name for c in case_items))))
    print("Packages:\t", ", ".join(list(set(p.name for p in packages))))
    print("Execs:\t\t", ", ".join(list(set(e.name for e in execs))))
    print("Services:\t", ", ".join(list(set(s.name for s in services))))
    print("Cron:\t\t", ", ".join(list(set(c.name for c in cron))))
    print("Files:\t\t", ", ".join(list(set(f.name for f in files))))
    print("")

    print("Starting validation of puppet objects:")

    # Verify all includes have a corresponding class to include.
    for i in includes:
        for c in classes:
            if i.name == c.name:
                break
        else:
            add_log(module_name, LOG_TYPE_ERROR, (0, 0),
                    "There was an include for %s but no class in the module" % i, "")

    # Verify all files exist in the module files directory.
    asset_files = os.listdir(module_dir + SPLIT_TOKEN + "files")

    for f in get_resource_type("file"):
        for i in f.items:
            name, value = i.split("=>")
            if name.rstrip() == "source":
                value = value.replace("puppet:///modules/" + module_name + "/", "").replace("'", "").replace(" ", "").replace(",", "")
                if value not in asset_files:
                    add_log(module_name, LOG_TYPE_ERROR, (0, 0), "Puppet file has non existing puppet source: " + i, str(f))
                    break
