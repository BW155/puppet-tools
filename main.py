import os
import time

from termcolor import colored

from constants import SPLIT_TOKEN, LOG_TYPE_FATAL, LOG_TYPE_ERROR, LOG_TYPE_WARNING, LOG_TYPE_INFO
from parser import walk_content
from puppet_objects.puppet_file import PuppetFile
from utility import get_file_contents, get_all_files, add_log, clear_logs, get_logs
from validate import process_puppet_module


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

    clear_logs()


def main(path, log_level=LOG_TYPE_WARNING, print_tree=False, only_parse=True):
    files = get_all_files(path)
    puppet_files = [f for f in files if f.endswith(".pp") and not f.split(SPLIT_TOKEN)[-1].startswith(".")]

    path = os.path.normpath(path)
    path = os.path.abspath(path)

    start = time.time()

    total = []

    for f in puppet_files:
        print(colored("Processing file: .%s" % f.replace(path, ""), 'cyan'))

        try:
            total.append(process_file(f))
        except Exception as e:
            import traceback
            add_log(f, LOG_TYPE_FATAL, (0, 0), "FATAL: Panic during file parsing, " + str(e), "")
            traceback.print_exc()

        print_logs(log_level)

    print("parsing took %f seconds" % (time.time() - start))

    if only_parse:
        return

    start = time.time()

    process_puppet_module(total, "ossec")
    print_logs(log_level)

    print("validating took %f seconds" % (time.time() - start))

    # if print_tree:
    #    for i in total:
    #        print(i)
    #        i.print_items()


if __name__ == '__main__':
    check_path = "./ossec-development"
    main(check_path, log_level=LOG_TYPE_ERROR, print_tree=False, only_parse=False)
