import os

from termcolor import colored

from constants import LOG_TYPE_ERROR, SPLIT_TOKEN, LOG_TYPE_FATAL, LOG_TYPE_WARNING, LOG_TYPE_DEBUG
from puppet_objects import PuppetObject
from puppet_objects.puppet_case_item import PuppetCaseItem
from puppet_objects.puppet_class import PuppetClass
from puppet_objects.puppet_include import PuppetInclude
from puppet_objects.puppet_resource import PuppetResource
from puppet_objects.puppet_variable import PuppetVariable
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


def validate_puppet_module(puppet_files, module_dir):
    print("\nValidating...")
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
    variables = get_type(PuppetVariable)

    class_names = [c.name for c in classes]
    module_name = class_names[0].split("::")[0]

    for cl in classes:
        if module_name not in cl.name:
            add_log(module_name, LOG_TYPE_WARNING, (0, 0),
                    "Please check the provided module name and/or classes, the module name should be in the class "
                    "names, found: '%s' while should start with '%s'" % (cl.name, module_name), "")

    # Summary
    print()
    print("Module '%s' Content Summary:" % module_name)
    print("Classes:\t", ", ".join(list(set(c.name for c in classes))))
    print("Case items:\t", ", ".join(list(set(c.name for c in case_items))))
    print("Packages:\t", ", ".join(list(set(p.name for p in packages))))
    print("Execs:\t\t", ", ".join(list(set(e.name for e in execs))))
    print("Services:\t", ", ".join(list(set(s.name for s in services))))
    print("Cron:\t\t", ", ".join(list(set(c.name for c in cron))))
    print("Files:\t\t", ", ".join(list(set(f.name for f in files))))
    print("Variables:\t", ", ".join(list(set(v.name for v in variables))))
    print()

    print("Starting validation of puppet objects:")

    # Verify all includes have a corresponding class to include.
    verify(verify_includes, {"includes": includes, "classes": classes, "module_name": module_name},
           "All includes have a corresponding class to include")

    # Verify all resource items
    verify(verify_resource_items, {"resources": get_type(PuppetResource), "module_name": module_name},
           "All resources have valid references")

    # Verify all resource item references
    verify(verify_resource_item_references, {
        "resources": get_type(PuppetResource),
        "services": services,
        "module_name": module_name,
        "execs": execs,
        "packages": packages,
        "files": files
    }, "All resources have valid items")

    # Verify all files exist in the module files directory.
    verify(verify_resource_file_sources, {"module_dir": module_dir,
                                          "file_resource_sources": get_resource_type("file"),
                                          "module_name": module_name},
           "All resource file sources are available in the module")


def verify(method, args, name):
    errors = method(**args)
    print(colored(("️❌" if errors else "✔") + " Verified " + name, "red" if errors else "green"))


def verify_includes(includes, classes, module_name):
    errors = False
    for i in includes:
        for c in classes:
            if i.name == c.name:
                break
        else:
            add_log(module_name, LOG_TYPE_ERROR, (0, 0),
                    "There was an include for %s but no class in the module" % i, "")
            errors = True
    return errors


def verify_resource_items(resources, module_name):
    errors = False
    for r in resources:
        for val in r.items:
            name, _ = val.split("=>")
            name = name.rstrip()

            if r.typ == "file":
                if name not in PuppetResource.ALLOWED_RESOURCE_FILE_ITEMS:
                    add_log(module_name, LOG_TYPE_ERROR, (r.line_number, 0),
                            "Resource '%s' item name %s not in allowed names for this resource type" % (r.typ, name),
                            str(r))
                    errors = True
            elif r.typ == "service":
                if name not in PuppetResource.ALLOWED_RESOURCE_SERVICE_ITEMS:
                    add_log(module_name, LOG_TYPE_ERROR, (r.line_number, 0),
                            "Resource '%s' item name %s not in allowed names for this resource type" % (r.typ, name),
                            str(r))
                    errors = True
            elif r.typ == "package":
                if name not in PuppetResource.ALLOWED_RESOURCE_PACKAGE_ITEMS:
                    add_log(module_name, LOG_TYPE_ERROR, (r.line_number, 0),
                            "Resource '%s' item name %s not in allowed names for this resource type" % (r.typ, name),
                            str(r))
                    errors = True
            elif r.typ == "exec":
                if name not in PuppetResource.ALLOWED_RESOURCE_EXEC_ITEMS:
                    add_log(module_name, LOG_TYPE_ERROR, (r.line_number, 0),
                            "Resource '%s' item name %s not in allowed names for this resource type" % (r.typ, name),
                            str(r))
                    errors = True
            elif r.typ == "cron":
                if name not in PuppetResource.ALLOWED_RESOURCE_CRON_ITEMS:
                    add_log(module_name, LOG_TYPE_ERROR, (r.line_number, 0),
                            "Resource '%s' item name %s not in allowed names for this resource type" % (r.typ, name),
                            str(r))
                    errors = True
            elif r.typ == "firewall":
                pass  # TODO: Implement
            else:
                add_log(module_name, LOG_TYPE_DEBUG, (r.line_number, 0), "Not Implemented verify resource type: '%s'" % r.typ, str(r))
    return errors


def find_any_path(resources, search_path):
    paths = list(
        set([p.replace("'", "").replace(",", "") for p in [r.get_value_for_item_name("path") for r in resources] if p]))

    for path in paths:
        if path == search_path:
            return True
    return False


def verify_resource_item_references(resources, services, files, execs, packages, module_name):
    errors = False

    service_names = [s.name for s in services]
    file_names = [f.name for f in files]
    exec_names = [e.name for e in execs]
    package_names = [p.name for p in packages]

    for r in resources:
        for val in r.items:
            _, value = val.split("=>")
            value = value.lstrip().replace(",", "").split("#")[0].rstrip()

            if value.startswith("Service"):
                service_name = value.replace("Service['", "").replace("']", "")
                if service_name not in service_names:
                    add_log(
                        module_name, LOG_TYPE_WARNING, (r.line_number, 0),
                        "Resource %s '%s' has a reference to Service '%s' but couldn't be found, may exist in parent "
                        "module" % (r.typ, r.name, service_name), str(r))
            elif value.startswith("File"):
                file_name = value.replace("File['", "").replace("']", "")

                if file_name not in file_names and not find_any_path(files, file_name):
                    add_log(
                        module_name, LOG_TYPE_WARNING, (r.line_number, 0),
                        "Resource %s '%s' has a reference to File '%s' but couldn't be found, may exist in parent "
                        "module" % (r.typ, r.name, file_name), str(r))
            elif value.startswith("Exec"):
                exec_name = value.replace("Exec['", "").replace("']", "")
                if exec_name not in exec_names:
                    add_log(
                        module_name, LOG_TYPE_WARNING, (r.line_number, 0),
                        "Resource %s '%s' has a reference to Exec '%s' but couldn't be found, may exist in parent "
                        "module" % (r.typ, r.name, exec_name), str(r))
            elif value.startswith("Package"):
                package_name = value.replace("Package['", "").replace("']", "")
                if package_name not in package_names:
                    add_log(
                        module_name, LOG_TYPE_WARNING, (r.line_number, 0),
                        "Resource %s '%s' has a reference to Package '%s' but couldn't be found, may exist in parent "
                        "module" % (r.typ, r.name, package_name), str(r))
            elif value.startswith("Stage"):
                add_log(module_name, LOG_TYPE_DEBUG, (r.line_number, 0), "Not Implemented Stage['.*']", str(r))
                pass  # TODO: Implement? what is it?
            elif value.startswith("template"):
                add_log(module_name, LOG_TYPE_DEBUG, (r.line_number, 0), "Not Implemented template['.*']", str(r))
                pass  # TODO: Implement template validation
            elif value.startswith("'"):
                pass
            elif value == "file":
                pass
            elif value == "directory":
                pass
            elif value == "true" or value == "false":
                pass
            elif value.isnumeric():
                pass
            elif value == "absent":
                pass
            elif value.startswith("[") and value.endswith("]"):
                pass
            else:
                add_log(module_name, LOG_TYPE_DEBUG, (r.line_number, 0), "Unimplemented resource item?", value)

    return errors


def verify_resource_file_sources(module_dir, file_resource_sources, module_name):
    asset_files = os.listdir(module_dir + SPLIT_TOKEN + "files")
    errors = False

    for f in file_resource_sources:
        for i in f.items:
            name, value = i.split("=>")
            if name.rstrip() == "source":
                value = value.replace("puppet:///modules/" + module_name + "/", "") \
                    .replace("'", "") \
                    .replace(" ", "") \
                    .replace(",", "")
                if value not in asset_files:
                    add_log(module_name, LOG_TYPE_ERROR, (f.line_number, 0), "Puppet file has non existing puppet source: " + i,
                            str(f))
                    errors = True
                    break
    return errors
