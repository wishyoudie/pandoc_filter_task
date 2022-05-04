import sys
from pandocfilters import *

header_storage = []


def get_header_content(value):
    """
    Get contents of a header in a single string
    """
    res = ""
    for i in value[2]:
        if i['t'] == 'Str':
            res = res + i['c']
        else:
            res = res + " "
    return res


def handle(key, value, format, meta):
    """
    Filter functions common call
    """
    find_repeated_headers(key, value, format, meta)
    change_headers(key, value, format, meta)
    change_word_bold(key, value, format, meta)


def find_repeated_headers(key, value, format, meta):
    """
    Find repeated headers and warn the user if found
    NB! Two headers are considered repeated if they have the same text and they are the same level
    """
    global header_storage
    if key == 'Header':
        if str(value[0]) + str(value[2]) in header_storage:
            sys.stderr.write(
                "WARNING | Repeated level " + str(value[0]) + " header: " + get_header_content(value) + "\n")
        else:
            header_storage.append(str(value[0]) + str(value[2]))
    return None


def change_headers(key, value, format, meta):
    """
    Change all headers with level less or equal to 3 to uppercase
    """
    def go(val):
        if val['t'] == 'Space':
            return val
        elif val['t'] == 'Str':
            return Str(val['c'].upper())
        else:
            for ind in range(len(val['c'])):
                val['c'][ind] = go(val['c'][ind])
            return val

    if key == 'Header' and value[0] <= 3:
        for i in range(len(value[2])):
            value[2][i] = go(value[2][i])
        return Header(value[0], value[1], value[2])


def change_word_bold(key, value, format, meta):
    """Change the word 'bold' in any place to bold format
    NB! Any case changes (bold, BOLD, bOLD etc.)
    """

    def go(val):
        if val['t'] == 'Space':
            return val
        elif val['t'] == 'Str':
            if val['c'].lower().count("bold") > 0:
                return Strong([Str(val['c'])])
            return Str(val['c'])
        else:
            for ind in range(len(val['c'])):
                val['c'][ind] = go(val['c'][ind])
            return val

    if key == 'Para':
        for i in range(len(value)):
            value[i] = go(value[i])
        return Para(value)

    elif key == 'Header':
        for i in range(len(value[2])):
            value[2][i] = go(value[2][i])
        return Header(value[0], value[1], value[2])

    elif key == 'BulletList':
        for i in range(len(value)):
            for j in range(len(value[i])):
                value[i][j] = go(value[i][j])
        return BulletList(value)

    elif key == 'OrderedList':
        for i in range(1, len(value[1])):
            for j in range(len(value[1][i])):
                value[1][i][j] = go(value[1][i][j])
        return OrderedList(value[0], value[1])

    else:
        sys.stderr.write(str(value) + "\n")
        return None

if __name__ == "__main__":
    toJSONFilter(handle)

# def debug(value):
#     res = ""
#     for i in value:
#         res = res + str(i) + "\n"
#     sys.stderr.write(res)