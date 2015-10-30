#! /usr/local/bin/python3
# coding=utf-8
#
# -----------------------------------------------------------------------------
#   file:       zygrid.py
#   use:
#
#   author:     dpomondo
#   site:       github.com/dpomondo/zyplot
# -----------------------------------------------------------------------------

home_dir = '/usr/self/bin/zyplot'
import sys
if home_dir not in sys.path:
    sys.path.append(home_dir)
import utils.zyutils as zyutils

def zygrid(*args, **kwargs):
    """ Takes lists, returns them formatted as a printable table.

        *args:      One list for each line of the table. Formatted either as
                    a tuple `(name, [x, x, ...])` or as a list with the first
                    item being the row name.
                    Row names can be `None` or empty strings.

        **kwargs    dictionary contaiing format specifications. 
        """
    
    row_names = list(zed[0] for zed in args)
    collected = []
    coll_widths = []
    for arg in args:
        collected.append(arg[1] if len(arg) == 2 else arg[1:])
        coll_widths.append(max(len(str(x)) for x in collected[-1] if x is not
                           None))

    row_name_width = max(list(len(x) for x in row_names if x is not None))
    if kwargs.get('box_width', None) is not None:
        box_width = kwargs['box_width']
    else:
        box_width = max(coll_widths)


