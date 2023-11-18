import os


def pathstr(*s: str) -> str:
    return os.path.abspath(os.path.expanduser(os.path.join(*s)))


def char2code(char):
    return format(ord(char), "#07x")[len("0x"):]
