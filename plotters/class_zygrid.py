#! /usr/local/bin/python3
# coding=utf-8
#
# -----------------------------------------------------------------------------
#   file:       class_zygrid.py
#   use:
#
#   author:     dpomondo
#   site:       github.com/dpomondo/zyplot
# -----------------------------------------------------------------------------


class Zygrid:
    """ takes multiple iterables, returns a list of formatted lines
    """
    def __init__(self, *iterables, **kwargs):
        self.data = iterables
        self.num_rows = len(self.data)
        self.num_cols = len(self.data[0])
        self.column_names = kwargs.get('column_names', [])
        self.row_names = kwargs.get('row_names', [])
        self.minimum_box_width = min_box_width(self.data,
                                               kwargs.get('buffer', 1),
                                               kwargs.get('color', False))
        self.kwargs = kwargs

    def __getattr__(self, attrname):
        if attrname in self.kwargs.keys():
            return self.kwargs[attrname]
        else:
            raise AttributeError(attrname)

    def __setattr__(self, attrname, value):
        """ reroute attribute assignment to common dictionary
        """
        self.kwargs[attrname] = value

    def __str__(self):
        return "[Grid Formatter Object, <{}> by <{}>]".format(self.num_rows,
                                                              self.num_cols)

    def min_box_width(iters, buffer=0, color=False):
        box_width = 0
        if color is False:
            for it in iters:
                for i in it:
                    if len(str(i)) > box_width:
                        box_width = len(str(i))
        else:
            # each object it in iters should be a 3-tuple, with a color
            # code as 0, the table entry as 1, and a color clear code as 2
            for it in iters:
                for i in it:
                    if len(str(i[1])) > box_width:
                        box_width = len(str(i[1]))
        return box_width + buffer

    def slicer(iters, start, end, row_flag=True):
        res = []
        if row_flag is True:
            for it in iters:
                res.append(it[start:end])
        else:
            for ind in range(len(iters[0])):
                res.append(list(its[ind] for its in iters))
        return res

    def temp_return_format():
        return('col_names', 'line', 'rows')

    
