from constants import LOG_TYPE_FATAL, CHECK_RESOURCE_FIRST_LINE, CHECK_RESOURCE_ITEM_POINTER, CHECK_RESOURCE_ITEM_VALUE, \
    CHECK_RESOURCE_ITEM_COMMA
from puppet_objects.puppet_block import PuppetBlock
from puppet_objects.puppet_case import PuppetCase
from puppet_objects.puppet_case_item import PuppetCaseItem
from puppet_objects.puppet_class import PuppetClass
from puppet_objects.puppet_resource import PuppetResource
from utility import strip_comments, brace_count_verify, add_log, get_until, get_matching_end_brace, count_newlines, \
    check_regex


def walk_content(content, puppet_file, index=0, line_number=1):
    content = strip_comments(content)
    result = brace_count_verify(content)
    if result == 0:
        block = walk_block(content, line_number, puppet_file)
        puppet_file.add_item(block)
    elif result < 0:
        add_log(puppet_file.name, LOG_TYPE_FATAL, (0, 0), "Too few start braces '{', file can't be parsed", "")
    elif result > 0:
        add_log(puppet_file.name, LOG_TYPE_FATAL, (0, 0), "Too few end braces '}', file can't be parsed", "")

    return puppet_file


def walk_block(content, line_number, puppet_file):
    puppet_block = PuppetBlock()
    index = 0

    while index < len(content):
        char = content[index]

        if char == '\n':
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
            items = [len(i) for i in ["package", "file", "service", "cron", "exec"]
                     if content[index:].startswith(i) and "=>" not in get_until(content[index:], "\n")[0]]
            if len(items) == 1:
                text, size = get_until(content[index:], "\n")
                if not check_regex(text, (line_number, 0), puppet_file, CHECK_RESOURCE_FIRST_LINE):
                    _, size = get_until(content[index:], '}')
                    index += size
                else:
                    item_len = items[0]
                    name = content[index:index + item_len]

                    index += item_len

                    _, size = get_until(content[index:], '{')
                    index += size

                    ind = get_matching_end_brace(content, index)
                    puppet_resource = walk_resource(content[index:ind], name, line_number, puppet_file)

                    puppet_block.add_item(puppet_resource)
                    line_number += count_newlines(content[index:ind])
                    index += ind - index + 1
            else:
                # print("not implemented: ", char)
                index += 1
    return puppet_block


def walk_class(content, name, line_number, puppet_file):
    puppet_class = PuppetClass(name)
    puppet_block = walk_block(content, line_number, puppet_file)
    puppet_class.add_item(puppet_block)
    return puppet_class


def walk_case(content, name, line_number, puppet_file):
    puppet_case = PuppetCase(name)
    index = 0

    while index < len(content):
        char = content[index]
        if char == "'":
            index += 1
            name, size = get_until(content[index:], "'")
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

        if char == '\n':
            # Found end of line
            line_number += 1
            index += 1
        elif char == '}':
            index += 1
        elif char != ' ':
            text, size = get_until(content[index:], "\n")
            if check_regex(text, (line_number, 0), puppet_file, CHECK_RESOURCE_ITEM_POINTER):
                if check_regex(text, (line_number, 0), puppet_file, CHECK_RESOURCE_ITEM_VALUE):
                    check_regex(text, (line_number, 0), puppet_file, CHECK_RESOURCE_ITEM_COMMA)
            puppet_resource.add_item(text)
            index += size
        else:
            index += 1
    return puppet_resource
