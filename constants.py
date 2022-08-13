import os
import re
SPLIT_TOKEN = "\\" if os.name == "nt" else "/"

CHECK_RESOURCE_FIRST_LINE = re.compile(r"[a-z]* *{ *'[\S ]*' *:")
CHECK_RESOURCE_ITEM_POINTER = re.compile(r"\S+[ ]*=>")
CHECK_RESOURCE_ITEM_VALUE = re.compile(r"\S+[ ]*=>[ ]*.*")
CHECK_RESOURCE_ITEM_COMMA = re.compile(r"\S+[ ]*=>[ ]*.*,")

LOG_TYPE_INFO = 'info'
LOG_TYPE_WARNING = "warning"
LOG_TYPE_ERROR = "error"
LOG_TYPE_FATAL = "fatal"
log_messages = {
    CHECK_RESOURCE_FIRST_LINE: (LOG_TYPE_ERROR, "Resource invalid"),
    CHECK_RESOURCE_ITEM_POINTER: (LOG_TYPE_ERROR, "Resource item does not have a valid format"),
    CHECK_RESOURCE_ITEM_VALUE: (LOG_TYPE_ERROR, "Resource item does not have a value"),
    CHECK_RESOURCE_ITEM_COMMA: (LOG_TYPE_ERROR, "Resource item does not have a comma at the end"),
}