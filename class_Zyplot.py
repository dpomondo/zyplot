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
        self.zyformat = self.return_format_dict()
        self.data = iterables
        for key in kwargs:
            self.zupdate(key, kwargs[key])

    # def __setattr__(self, attrname, value):
    #     if attrname in self.zyformat.keys():
    #         self.zupdate(attrname, value)
    #     else:
    #         object.__setattr__(self, attrname, value)

    def __str__(self):
        return "<{} instance, {} by {}>".format(
            self.__class__.__name__,
            self.width,
            self.length)

    def zupdate(self, key, value):
        if key in self.zyformat.keys():
            self.zyformat[key] = value
        #  else:
            #  raise KeyError

    @property
    def width(self):
        """ Return number of columns in self.data.
        """
        return (len(self.data[0]) if self.zyformat.get('row_flag', True)
                is True else len(self.data))

    @property
    def length(self):
        """ Return number of rows in self.data.
        """
        return (len(self.data[0]) if self.zyformat.get('row_flag', True)
                is False else len(self.data))

    @property
    def depth(self):
        """ Return how many columns each column name refers to.
        """
        if self.zyformat.get('column_names', None) is None:
            return 1
        else:
            return self.width / len(self.zyformat['column_names'])

    def return_format_dict(self):
        """ Return a dictionary of formatting arguments.

            This exists to be overloaded. Subclasses of Zyplot will have their
            own formatting dictionaries, containing default values and/or
            functions.
            """
        return {'row_flag':     True
                }


class ZyplotTester(Zyplot):
    def __init__(self, iterables, **kwargs):
        Zyplot.__init__(self, iterables, **kwargs)

    def __str__(self):
        result = "<{}, {} instance, {} by {}".format(
            __name__,
            self.__class__.__name__,
            self.width, 
            self.length)
        for key in sorted(self.zyformat.keys()):
            result += "\n\t{}={}".format(key, self.zyformat[key])
        return result

    def return_format_dict(self):
        return {'a':    'zabba',
                'b':    'bazza',
                'c':    'yabba'
                }

if __name__ == '__main__':
    zed = ZyplotTester(list(range(10)), a='thunder')
    print(zed)
    zed.zupdate('b', 'eagles')
    print(zed)
