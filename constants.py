import os
import re
from enum import Enum

SPLIT_TOKEN = "\\" if os.name == "nt" else "/"


class CheckRegex(Enum):
    CHECK_RESOURCE_FIRST_LINE = 1
    CHECK_RESOURCE_ITEM_POINTER = 2
    CHECK_RESOURCE_ITEM_VALUE = 3
    CHECK_RESOURCE_ITEM_COMMA = 4
    CHECK_RESOURCE_ITEM_COMMA_WARN = 5
    CHECK_RESOURCE_ITEM_COMMA_NEXT_LINE_END = 6


check_regex_list = {
    CheckRegex.CHECK_RESOURCE_FIRST_LINE: re.compile(r"[a-z]* *{ *'[\S ]*' *:"),
    CheckRegex.CHECK_RESOURCE_ITEM_POINTER: re.compile(r"\S+[ ]*=>"),
    CheckRegex.CHECK_RESOURCE_ITEM_VALUE: re.compile(r"\S+[ ]*=>[ ]*.*"),
    CheckRegex.CHECK_RESOURCE_ITEM_COMMA: re.compile(r"\S+[ ]*=>[ ]*.*,"),
    CheckRegex.CHECK_RESOURCE_ITEM_COMMA_WARN: re.compile(r"\S+[ ]*=>[ ]*.*,"),
    CheckRegex.CHECK_RESOURCE_ITEM_COMMA_NEXT_LINE_END: re.compile(r"\S+ *=>.* *}")
}

LOG_TYPE_IGNORE = 0
LOG_TYPE_DEBUG = 1
LOG_TYPE_INFO = 2
LOG_TYPE_WARNING = 3
LOG_TYPE_ERROR = 4
LOG_TYPE_FATAL = 5

log_messages = {
    CheckRegex.CHECK_RESOURCE_FIRST_LINE: (LOG_TYPE_ERROR, "Resource invalid"),
    CheckRegex.CHECK_RESOURCE_ITEM_POINTER: (LOG_TYPE_ERROR, "Resource item does not have a valid format"),
    CheckRegex.CHECK_RESOURCE_ITEM_VALUE: (LOG_TYPE_ERROR, "Resource item does not have a value"),
    CheckRegex.CHECK_RESOURCE_ITEM_COMMA: (LOG_TYPE_ERROR, "Resource item does not have a comma at the end"),
    CheckRegex.CHECK_RESOURCE_ITEM_COMMA_WARN: (LOG_TYPE_WARNING, "Resource item does not end with a comma, styling issue"),
    CheckRegex.CHECK_RESOURCE_ITEM_COMMA_NEXT_LINE_END: (LOG_TYPE_IGNORE, "Resource item ends the resource but does not have a comma at the end"),
}