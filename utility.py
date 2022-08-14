import os
import re

from constants import log_messages, CheckRegex, check_regex_list

log_list = []


def strip_comments(code):
    code = str(code)
    return re.sub(r'(?m)^ *#.*\n?', '\n', code)


def add_log(file_name, typ, line_col, message, string):
    global log_list
    log_list.append((file_name, typ, line_col, message, string))


def clear_logs():
    global log_list
    log_list = []


def get_logs():
    return log_list


def check_regex(string, line_col, file, check_regex: CheckRegex):
    pattern = check_regex_list[check_regex]
    success = bool(pattern.match(string))
    if not success:
        log_type, message = log_messages[check_regex]
        add_log(file.name, log_type, line_col, message, string)
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


def find_next_string(content, string):
    index = 0
    while content[index:index + len(string)] != string:
        index += 1
    return index


def get_until(content, char=None, string=None):
    size = 0
    if char:
        size = find_next_char(content, char)
    elif string:
        size = find_next_string(content, string)
    return content[:size], size


def brace_count_verify(content):
    return content.count('{') - content.count('}')


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
