#! /usr/local/bin/python3
# coding=utf-8
#
# -----------------------------------------------------------------------------
#   file:       zyutils.py
#   use:
#
#   author:     dpomondo
#   site:       github.com/dpomondo/zyplot
# -----------------------------------------------------------------------------

import subprocess


def get_terminal_info(arg):
    """ does what it says: returns terminal info given by arg.

    Stolen from:
    http://www.brandonrubin.me/2014/03/18/python-snippet-get-terminal-width/
    """
    command = ['tput', arg]
    try:
        result = int(subprocess.check_output(command))
    except OSError as e:
        print("Invalid Command '{0}': exit status ({1})".format(
              command[0], e.errno))
    except subprocess.CalledProcessError as e:
        print("Command '{0}' returned non-zero exit status: ({1})".format(
              command, e.returncode))
    else:
        return result


def get_terminal_height():
    return get_terminal_info('lines')


def get_terminal_width():
    return get_terminal_info('cols')


def indexer_maker(mn, mx, bar_height):
    """ returns a function that returns the vertical index of an input.

        mn:     minimum value in the set
        mx:     maximum value in the set
        bar_height:
                number of lines in the column

        Can take None values and returns None.
        """
    def indexer(_x):
        if _x is None:
            return None
        elif bar_height > 1 and mx - mn > 0:
            return ((bar_height - 1) -
                    int((_x - mn) / (mx - mn) * (bar_height - 1)))
        else:
            return 0
    return indexer


def dict_to_obj(dic):
    """ Returns an object with a given dictionary's keys as attributes.

        Some functions get passed in objects with with large functions as
        attributes. For the sake of consistency, dictionaries are turned into
        similar objects. This may not be a necessary step.
        """
    class Empty():
        pass
    temp = Empty()
    for key in dic:
        setattr(temp, key, dic[key])
    return temp
