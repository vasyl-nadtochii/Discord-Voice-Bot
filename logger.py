from colorama import Fore
from colorama import Style

from enum import Enum

class MessageType(Enum):
    info = "INFO:"
    debug = "DEBUG:"
    error = "ERROR:"
    warning = "WARNING:"
    common = str()

def log(message: str, type: MessageType = MessageType.common):
    if type == MessageType.common:
        print(message)
    else:
        color = None
        if type == MessageType.info:
            color = Fore.GREEN
        elif type == MessageType.debug:
            color = Fore.MAGENTA
        elif type == MessageType.error:
            color = Fore.RED
        elif type == MessageType.warning:
            color = Fore.YELLOW

        print(f"{ color }{ type.value } { message }{ Style.RESET_ALL }")