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
    def __init__(self, *iterables, **kwargs):
        self.data = iterables
        self.__dynamic_attrs = {}
        self.__func_attrs = {}
        self.__fixed_attrs = []
        da, fa = self.return_dynamic_attrs(), self.return_fixed_attrs()
        for key, value in da:
            self.__dynamic_attrs[key] = value
        for key, value in fa:
            self.__func_attrs[key] = value
        self.__fixed_attrs.extend(self.return_fixed_attrs())
        for key, value in kwargs:
            setattr(self, key, value)

    def return_dynamic_attrs(self):
        """ This exists to get overloaded """
        return {}

    def return_func_attrs(self):
        """ This exists to get overloaded """
        return {}

    def return_fixed_attrs(self):
        """ This exists to get overloaded """
        return []

    def __setattr__(self, attrname, value):
        if attrname in self.__func_attrs.keys():
            # slf.__func_attrs(value) should be a method which will be
            # called by __getattr__
            object.__setattr__(self, attrname, self.__func_attrs[value])
        elif attrname in self.__dynamic_attrs.keys():
            object.__setattr__(self, attrname, value)
        elif attrname in self.__fixed_attrs:
            object.__setattr__(self, attrname, value)
        else:
            raise ValueError("{} not a valid keyword".format(attrname))

    def __getattr__(self, attrname):
        if attrname in self.__func_attrs.keys():
            return self.__dict__[attrname]()
        if attrname in self.__dynamic_attrs.keys():
            return self.__dict__[attrname]
        if attrname in self.__fixed_attrs:
            return self.__dict__[attrname]
        else:
            raise KeyError


def ZyplotTester(Zyplot):
    def __init__(self, *iterables, **kwargs):
        pass

    def return_dynamic_attrs(self):
        """ This exists to get overloaded """
        return {}

    def return_func_attrs(self):
        """ This exists to get overloaded """
        return {}

    def return_fixed_attrs(self):
        """ This exists to get overloaded """
        return []
