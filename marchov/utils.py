def normalize_nick(nick):
    output = nick.strip("_@+ ").lower()
    output = output.replace("[m]", "")
    return output
