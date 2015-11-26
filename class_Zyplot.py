#! /usr/local/bin/python3
# coding=utf-8
#
# -----------------------------------------------------------------------------
#   file:       class_zyplot.py
#   use:
#
#   author:     dpomondo
#   site:       github.com/dpomondo/zyplot
# -----------------------------------------------------------------------------


class Zyplot:
    """ Take iterables and store them in a form ready to be formatted.
        """
    def __init__(self, iterables, **kwargs):
        self.data = iterables
        self.__format = self.return_format_dict()
        for key in kwargs:
            if key in self.__format.keys():
                self.__format[key] = kwargs[key]

    def width(self):
        """ Return number of columns in self.data.
            """
        return (len(self.data[0]) if self.__format['row_flag'] is True else
                len(self.data))

    def length(self):
        """ Return number of rows in self.data.
            """
        return (len(self.data[0]) if self.__format['row_flag'] is False else
                len(self.data))

    def depth(self):
        """ Return how many columns each column name refers to.
        """
        if self.__format.get('column_names', None) is None:
            return 1
        else:
            return self.width() / len(self.__format['column_names'])

    def return_format_dict(self):
        """ Return a dictionary of formatting arguments.

            This exists to be overloaded. Subclasses of Zyplot will have their
            own formatting dictionaries, containing default values and/or
            functions.
            """
        return {'row_flag':     True
                }
