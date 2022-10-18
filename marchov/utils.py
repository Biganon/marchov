from unidecode import unidecode
import re


def normalize_nick(nick):
    output = nick.strip("_@+ ").lower()
    output = output.replace("[m]", "")
    return output


def normalize_lover(lover):
    output = lover.strip().lower()
    output = unidecode(output)
    output = re.sub(r"[^a-z0-9]", "", output)
    return output
