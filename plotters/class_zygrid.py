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
    def __init__(self, iterables, **kwargs):
        self.data = iterables
        self.row_flag = kwargs.get('rows', True)
        self.column_names = kwargs.get('column_names', None)
        self.row_names = kwargs.get('row_names', None)
        self.kwargs = kwargs

    def __getattr__(self, attrname):
        if attrname == 'width':
            return (len(self.data[0]) if self.row_flag is True else
                    len(self.data))
        elif attrname == 'length':
            return (len(self.data[0]) if self.row_flag is False else
                    len(self.data))
        elif attrname == 'minimum_box_width':
            return self.min_box_width(self.data,
                                      self.kwargs.get('buffer', 1),
                                      self.kwargs.get('color', False))
        elif attrname == 'box_width':
            # the behavior of this is... problematic
            return self.return_box_width()
        elif attrname in self.kwargs.keys():
            return self.kwargs[attrname]
        else:
            return self.__dict__[attrname]

    def __setattr__(self, attrname, value):
        if attrname in ['width', 'length', 'minimum_box_width']:
            return
        elif attrname == 'column_names':
            self.set_column_names(value)
        elif attrname == 'row_names':
            self.set_row_names(value)
        elif attrname == 'box_width':
            value = max(value, self.minimum_box_width)
            object.__setattr__(self, attrname, value)
        else:
            object.__setattr__(self, attrname, value)

    def __len__(self):
        if self.row_flag is False:
            return len(self.data[0])
        else:
            return len(self.data)

    def __getitem__(self, ind):
        if self.row_flag is True:
            return self.data[ind]
        else:
            if isinstance(ind, int):
                return list(its[ind] for its in self.data)
            if isinstance(ind, slice):
                temp = []
                step = ind.step if ind.step is not None else 1
                start = ind.start if ind.start is not None else 0
                stop = ind.stop if ind.stop is not None else len(self)
                if step < 0:
                    start, stop = stop - 1, start - 1
                for jind in range(start, stop, step):
                    temp.append(list(its[jind] for its in self.data))
            else:
                raise TypeError("{}".format(type(ind)) +
                                " cannot be used to index Zygrid object")
            return temp

    def __str__(self):
        return "[Zygrid Formatter Object, <{}> by <{}>]".format(self.width,
                                                                self.length)

    def set_column_names(self, cols):
        if cols is None:
            object.__setattr__(self, 'column_names', None)
            #  self.column_names = []
        else:
            if len(cols) != self.width:
                raise ValueError("Number of column names should equal number" +
                                 " of columns")
            #  self.column_names = cols
            object.__setattr__(self, 'column_names', cols[:])

    def set_row_names(self, rws):
        if rws is None:
            object.__setattr__(self, 'row_names', None)
            #  self.row_names = []
        else:
            if len(rws) != self.length:
                raise ValueError("Number of row names should equal number" +
                                 " of rows")
            #  self.row_names = cols
            object.__setattr__(self, 'row_names', rws[:])

    def return_format_func(self):
        if self.kwargs.get('color', None) is not None:
            return lambda x: "{}{:^{wid}}{}".format(*x, wid=self.box_width)
        else:
            return lambda x: "{:^{wid}}".format(str(x), wid=self.box_width)

    def min_list_size(self, iters):
        return min(list(len(str(i)) for i in iters))

    def min_box_width(self, iters, buffer=0, color=False):
        temp_box_width = 0
        if color is False:
            for it in iters:
                #  for i in it:
                    #  if len(str(i)) > temp_box_width:
                        #  temp_box_width = len(str(i))
                temp_box_width = max(temp_box_width, self.min_list_size(it))
        else:
            # each object it in iters should be a 3-tuple, with a color
            # code as 0, the table entry as 1, and a color clear code as 2
            for it in iters:
                #  for i in it:
                    #  if len(str(i[1])) > temp_box_width:
                        #  temp_box_width = len(str(i[1]))
                temp_box_width = max(temp_box_width,
                                     self.min_list_size(
                                         list(i[1] for i in it)))
        return temp_box_width + buffer

    def return_box_width(self):
        #  return max(self.kwargs.get('box_width', 1), self.minimum_box_width)
        return self.kwargs.get('box_width',
                               self.__dict__.get('box_width',
                                                 self.minimum_box_width))

    def temp_return_format(self):
        return('col_names', 'line', 'rows', 'blank')

    def return_keys(self):
        return self.kwargs.keys()
