import os
import re
import time
from re import Pattern

from constants import SPLIT_TOKEN
from puppet_block import PuppetBlock
from puppet_case import PuppetCase
from puppet_case_item import PuppetCaseItem
from puppet_class import PuppetClass, PuppetFile
from puppet_resource import PuppetResource





CHECK_RESOURCE_ITEM_POINTER = re.compile(r"\S+[ ]*=>")
CHECK_RESOURCE_ITEM_VALUE = re.compile(r"\S+[ ]*=>[ ]*.*")
CHECK_RESOURCE_ITEM_COMMA = re.compile(r"\S+[ ]*=>[ ]*.*,")

LOG_TYPE_INFO = 'info'
LOG_TYPE_WARNING = "warning"
LOG_TYPE_ERROR = "error"
log_messages = {
    CHECK_RESOURCE_ITEM_POINTER: (LOG_TYPE_ERROR, "Resource item does not have a valid format"),
    CHECK_RESOURCE_ITEM_VALUE: (LOG_TYPE_ERROR, "Resource item does not have a value"),
    CHECK_RESOURCE_ITEM_COMMA: (LOG_TYPE_ERROR, "Resource item does not have a comma at the end"),
}


log_list = []


def add_log(file_name, typ, line_col, message):
    global log_list
    log_list.append((file_name, typ, line_col, message))


def check_regex(string, line_col, file, pattern: Pattern):
    success = bool(pattern.match(string))
    if not success:
        log_type, message = log_messages[pattern]
        add_log(file.name, log_type, line_col, message)
    return success


def get_all_files(path, include_dirs=False):
    path = os.path.normpath(path)
    path = os.path.abspath(path)
    print("Path: ", path)
    res = []
    for root, dirs, files in os.walk(path, topdown=True):
        if include_dirs:
            res += [os.path.join(root, d) for d in dirs]
        res += [os.path.join(root, f) for f in files]

    return res


def get_file_contents(path):
    with open(path, 'r') as f:
        return f.read()


def find_next_char(content, char):
    index = 0
    while content[index] != char:
        index += 1
    return index


def get_until(content, char):
    size = find_next_char(content, char)
    return content[:size], size


def get_matching_end_brace(content, index):
    if content[index] != '{':
        raise Exception("char is not a {, found: '%s'" % content[index])
    counter = 0
    end_brace_found = False
    try:
        while counter != 0 or not end_brace_found:
            if content[index] == '{':
                counter += 1
            if content[index] == '}':
                counter -= 1
                end_brace_found = True
            index += 1
    except IndexError as e:
        print(counter, end_brace_found)
        raise IndexError(str(e) + ": " + str(counter) + " " + str(end_brace_found))
    return index


def count_newlines(content):
    return len(content.split('\n'))


def walk_content(content, puppet_file, index=0, line_number=1):
    # print("Walking file:", puppet_file.name)
    block = walk_block(content, line_number, puppet_file)
    puppet_file.add_item(block)
    return puppet_file


def walk_block(content, line_number, puppet_file):
    #print("Walk Block:", line_number)
    puppet_block = PuppetBlock()
    index = 0

    while index < len(content):
        char = content[index]

        if char == '#':
            # Found comment
            size = find_next_char(content[index:], '\n')
            index += size
        elif char == '\n':
            # Found end of line
            line_number += 1
            index += 1
        elif content[index:index+4] == "case":
            index += 5  # include space after 'case'
            name, size = get_until(content[index:], ' ')
            _, size = get_until(content[index:], '{')
            index += size

            ind = get_matching_end_brace(content, index)
            puppet_case = walk_case(content[index:ind], name, line_number, puppet_file)

            puppet_block.add_item(puppet_case)
            line_number += count_newlines(content[index:ind])
            index += ind - index
        elif content[index:index+5] == "class":
            # Found class beginning
            index += 6  # include space after 'class'
            name, size = get_until(content[index:], ' ')
            index += size

            _, size = get_until(content[index:], '{')
            index += size
            ind = get_matching_end_brace(content, index)
            puppet_class = walk_class(content[index:ind], name, line_number, puppet_file)

            puppet_block.add_item(puppet_class)
            line_number += count_newlines(content[index:ind])
            index += ind - index
        else:
            items = [len(i) for i in ["package", "file", "service", "cron", "exec"] if content[index:].startswith(i)]
            if len(items) == 1:
                item_len = items[0]
                name = content[index:index + item_len]
                index += item_len
                _, size = get_until(content[index:], '{')
                index += size
                ind = get_matching_end_brace(content, index)
                puppet_resource = walk_resource(content[index:ind], name, line_number, puppet_file)

                puppet_block.add_item(puppet_resource)
                line_number += count_newlines(content[index:ind])
                index += ind - index
            # print("not implemented: ", char)
            index += 1
    return puppet_block


def walk_class(content, name, line_number, puppet_file):
    # print("Walk Class:", name, line_number)
    puppet_class = PuppetClass(name)
    puppet_block = walk_block(content, line_number, puppet_file)
    puppet_class.add_item(puppet_block)
    return puppet_class


def walk_case(content, name, line_number, puppet_file):
    # print("Walk Case:", name, line_number)
    puppet_case = PuppetCase(name)
    index = 0

    while index < len(content):
        char = content[index]
        if char == "'":
            index += 1
            name, size = get_until(content[index:], "'")
            # print("Case Name: ", name)
            index += size
            _, size = get_until(content[index:], ':')
            index += size

            _, size = get_until(content[index:], '{')
            index += size
            ind = get_matching_end_brace(content, index)

            puppet_case_item = PuppetCaseItem(name)
            puppet_block = walk_block(content[index:ind], line_number, puppet_file)
            puppet_case_item.add_item(puppet_block)
            puppet_case.add_item(puppet_case_item)
            line_number += count_newlines(content[index:ind])
            index += ind - index + 1
        elif char == '\n':
            line_number += 1
            index += 1
        else:
            index += 1

    return puppet_case


def walk_resource(content, typ, line_number, puppet_file):
    puppet_resource = PuppetResource(typ)
    index = 0

    _, size = get_until(content[index:], "'")
    index += size + 1
    name, size = get_until(content[index:], "'")
    puppet_resource.name = name
    index += size
    _, size = get_until(content[index:], ':')
    index += size + 1

    while index < len(content):
        char = content[index]

        if char == '#':
            # Found comment
            size = find_next_char(content[index:], '\n')
            index += size
        elif char == '\n':
            # Found end of line
            line_number += 1
            index += 1
        elif char == '}':
            index += 1
        elif char != ' ':
            # print(content[index:], '\n' in content[index:])
            text, size = get_until(content[index:], "\n")
            if check_regex(text, (line_number, 0), puppet_file, CHECK_RESOURCE_ITEM_POINTER):
                if check_regex(text, (line_number, 0), puppet_file, CHECK_RESOURCE_ITEM_VALUE):
                    check_regex(text, (line_number, 0), puppet_file, CHECK_RESOURCE_ITEM_COMMA)
            puppet_resource.add_item(text)
            index += size
        else:
            index += 1
    return puppet_resource


def process_file(path) -> PuppetFile:
    content = get_file_contents(path)
    puppet_file = PuppetFile(path)
    walk_content(content, puppet_file)
    return puppet_file


def main(path):
    global log_list
    files = get_all_files(path)
    puppet_files = [f for f in files if f.endswith(".pp") and not f.split(SPLIT_TOKEN)[-1].startswith(".")]
    start = time.time()

    path = os.path.normpath(path)
    path = os.path.abspath(path)

    for f in puppet_files:
        print("Processing file: .%s" % f.replace(path, ""))
        try:
            process_file(f)
        except Exception as e:
            print("FATAL ERROR:")
            print(e)
        for log_item in log_list:
            print(log_item)
        log_list = list()

    print("parsing took %f seconds" % (time.time() - start))


if __name__ == '__main__':
    check_path = "./ossec-development"
    main(check_path)
