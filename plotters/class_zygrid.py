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
        self.data = self.clean_inputs(iterables, kwargs.get('rows', True))
        self.num_rows = len(self.data)
        self.num_cols = len(self.data[0])
        self.column_names = kwargs.get('column_names', [])
        self.row_names = kwargs.get('row_names', [])
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

    def clean_inputs(self, iterables, row_flag):
        """
        """
        if row_flag is False:
            res = []
            for i in range(len(iterables[0])):
                res.append([])

            for ziter in iterables:
                for ind in range(len(ziter)):
                    res[ind].append(ziter[ind])
            return res
        else:
            return iterables
