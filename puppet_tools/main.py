import os
import time
import argparse

from termcolor import colored

from constants import SPLIT_TOKEN, LOG_TYPE_FATAL, LOG_TYPE_ERROR, LOG_TYPE_WARNING, LOG_TYPE_INFO, LOG_TYPE_DEBUG
from parser import walk_content
from puppet_objects.puppet_file import PuppetFile
from utility import get_file_contents, get_all_files, add_log, clear_logs, get_logs, logs_contains_error
from validate import validate_puppet_module


PARSER_ERROR = False
VALIDATION_ERROR = False


def process_file(path) -> PuppetFile:
    content = get_file_contents(path)
    puppet_file = PuppetFile(path)
    walk_content(content, puppet_file)
    return puppet_file


def print_logs(log_level=1):
    for log_item in get_logs():
        typ = log_item[1]
        if typ >= log_level:
            if typ == LOG_TYPE_FATAL:
                print(colored(log_item, 'white', 'on_red'))
            if typ == LOG_TYPE_ERROR:
                print(colored(log_item, 'red'))
            if typ == LOG_TYPE_WARNING:
                print(colored(log_item, 'yellow'))
            if typ == LOG_TYPE_INFO:
                print(colored(log_item, 'white'))
            if typ == LOG_TYPE_DEBUG:
                print(colored(log_item, 'cyan'))

    clear_logs()


def parse(puppet_files, path, log_level):
    global PARSER_ERROR
    total = []
    start = time.time()

    for f in puppet_files:
        print(colored("Processing file: .%s" % f.replace(path, ""), 'cyan'))

        try:
            total.append(process_file(f))
        except Exception as e:
            import traceback
            add_log(f, LOG_TYPE_FATAL, (0, 0), "FATAL: Panic during file parsing, " + str(e), "")
            traceback.print_exc()

        if logs_contains_error():
            PARSER_ERROR = True

        print_logs(log_level)

    print("parsing took %f seconds" % (time.time() - start))
    return total


def main(path, log_level=LOG_TYPE_WARNING, print_tree=False, only_parse=True):
    files = get_all_files(os.path.join(path, "manifests"))
    puppet_files = [f for f in files if f.endswith(".pp") and not f.split(SPLIT_TOKEN)[-1].startswith(".")]

    path = os.path.normpath(path)
    path = os.path.abspath(path)

    total = parse(puppet_files, path, log_level)

    if print_tree:
        for i in total:
            print(i)
            i.print_items()

    if only_parse:
        return

    start = time.time()

    validate_puppet_module(total, path)

    global VALIDATION_ERROR
    if logs_contains_error():
        VALIDATION_ERROR = True

    print_logs(log_level)

    print("validating took %f seconds" % (time.time() - start))
    print()
    print(colored("Parsing:\tERROR", "red") if PARSER_ERROR else colored("Parsing:\tSuccess", "green"))
    print(colored("Validation:\tERROR", "red") if VALIDATION_ERROR else colored("Validation:\tSuccess", "green"))


def entry():
    my_parser = argparse.ArgumentParser(
        description="Puppet Tools, including parser, linter and validator functions"
    )

    my_parser.add_argument("-t",
                           "--print-tree",
                           action='store_true',
                           help="Print the tree of parsed objects")

    my_parser.add_argument("-p",
                           "--only-parse",
                           action='store_true',
                           help="Only parse for format validating/linting")

    my_parser.add_argument("-l",
                           "--log-level",
                           type=int,
                           default=LOG_TYPE_WARNING,
                           help="Set minimum log level (Info=2, Warning=3, Error=4, Fatal=5)")

    my_parser.add_argument("Path",
                           metavar="path",
                           type=str,
                           help="the path to a puppet module")

    args = my_parser.parse_args()

    check_path = args.Path

    if not os.path.isdir(check_path):
        print("The path specified does not exist")
        exit(1)

    if not os.path.exists(os.path.join(check_path, "files")) or not \
            os.path.exists(os.path.join(check_path, "manifests")):
        print("Not a valid puppet module structure at path")
        exit(1)

    main(check_path, log_level=args.log_level, print_tree=args.print_tree, only_parse=args.only_parse)


if __name__ == '__main__':
    entry()
