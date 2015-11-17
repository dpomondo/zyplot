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
    """ Return a list of lines, formatted from a matrix of iterables.

        *iterables:     Multiple same-length lists or tuples. These can be
                        either rows or columns depending on whether the 'row'
                        arg in kwargs is True or False.
        *kwargs:        Formatting args, passed in as a dictionary. Options
                        include:
                        True/False options:
                        'row_flag':     
                                    whether *iterables are to be formatted as
                                    rows or columns.
                        'color':    whether each box is formatted with itself,
                                    or with an optional passed in color
                                    function.
                        Options with arguments:
                        'wrap':     whether or not rows are wrapped after
                                    a certain length.
                                    Options:
                                        int: wrap after that many columns
                                        'max': wrap after as many columns
                                        will fit on terminal screen
                        'column_names':
                                    optional column names
                        'column_widths':
                                    Specify how column widths are calculated.
                                    Default is 'minimum'.
                                    Options:
                                        'minimum': uses smallest width that
                                        fits the largest item for all coumns.
                                        'flexible': each column is as wide as
                                        needed to fit the largest item.
                                        integer: each coumn will be the largest
                                        of either the value of 'minimum' or the
                                        passed-in integer.
                                        NOTE: this conflicts with 'box_width'
                                        cos I am dumb.
                                        'columns': uses the width of column
                                        names. Defaults to 'flexible' if no
                                        column names given.
                        'column_padding':
                                    Extra width for added to coumns.
                        'column_names_trim_func':
                                    function used to trim column names longer
                                    than box_width
                        'row_names':    optional row names
                        'box_width':    otherwise box_width will be set as
                                    a function of the widest item
                        'table_padding': padding of blank spaces to the right 
                                    and left of the formatted table
                        'table_justification':
                                    'right': table formatted to right margin
                                    'center': table centered
                                    'left' or None: formatted to left margin
        """
    def __init__(self, iterables, **kwargs):
        self.data = iterables
        # mebbe 'rows' as kwarg for 'row_flag' is a bad idea...
        self.row_flag = kwargs.get('row_flag', True)
        # both column_names and row_names get routed to functions to set their
        # values
        self.column_names = kwargs.get('column_names', None)
        self.row_names = kwargs.get('row_names', None)
        # the following are `magic` for now:
        self.wrap = False
        self.start = 0
        self.step = self.stop = self.width
        # and we store the rest for later
        self.padding = kwargs.get('padding', 1)
        self.kwargs = kwargs

    def __getattr__(self, attrname):
        if attrname == 'width':
            return (len(self.data[0]) if self.row_flag is True else
                    len(self.data))
        elif attrname == 'length':
            return (len(self.data[0]) if self.row_flag is False else
                    len(self.data))
        elif attrname == 'minimum_box_width':
            return self.min_box_width(self.data, self.padding,
                                      self.kwargs.get('color', False))
        elif attrname == 'box_width':
            # the behavior of this is... problematic
            return self.return_box_width()
        elif attrname in self.kwargs.keys():
            return self.kwargs[attrname]
        elif attrname in self.__dict__.keys():
            return self.__dict__[attrname]
        else:
            raise KeyError(attrname)

    def __setattr__(self, attrname, value):
        if attrname in ['width', 'length', 'minimum_box_width']:
            return
        elif attrname == 'column_names':
            self.set_column_names(value)
        elif attrname == 'row_names':
            self.set_row_names(value)
        elif attrname == 'padding':
            value = max(1, value)
            object.__setattr__(self, attrname, value)
        elif attrname == 'row_flag':
            if value not in (True, False):
                raise ValueError(value)
            if value != self.__dict__.get('row_flag', True):
                object.__setattr__(self, attrname, value)
                temp = self.column_names
                self.set_column_names(self.row_names)
                self.set_row_names(temp)
            else:
                object.__setattr__(self, attrname, value)
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

    def min_box_width(self, iters, padding=0, color=False):
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
        return temp_box_width + padding

    def return_box_width(self):
        #  return max(self.kwargs.get('box_width', 1), self.minimum_box_width)
        return self.kwargs.get('box_width',
                               self.__dict__.get('box_width',
                                                 self.minimum_box_width))
    
    def get_column_widths(self):
        """ Creates a list of ints for use in formatting columns.    """
        #  if not hasattr(self, 'column_widths'):
        if ('column_widths' not in self.kwargs.keys() and 'column_widths' not
                in self.__dict__.keys()):
            self.column_widths = self.kwargs.get('column_widths', 'minimum')
        temp_widths = []
        if self.column_widths == 'minimum':
            for i in range(self.stop - self.start):
                temp_widths.append(self.minimum_box_width)
        elif isinstance(self.column_widths, int):
            # here we need to integrate self.box_width properly...
            temp = max(self.minimum_box_width, self.column_widths)
            for i in range(self.stop - self.start):
                temp_widths.append(temp)
        elif self.column_widths == 'columns':
            if self.column_names is None:
                # this is a terrible solution and must be fixed...
                self.column_widths = 'flexible'
            else:
                for nam in self.column_names:
                    temp_widths.append(len(nam) + self.padding)
        elif self.column_widths == 'flexible':
            if self.row_flag is False:
                #  raise NotImplementedError
                for i in range(self.stop - self.start):
                    temp.widths.append(
                        max(len(str(zit)) for zit in self.data[i]) +
                        self.padding)
            else:
                for i in range(self.stop - self.start):
                    temp_widths.append(
                        max(len(str(zit[i])) for zit in self.data) +
                        self.padding)
        return temp_widths

    def temp_return_format(self):
        return('col_names', 'line', 'rows', 'blank')

    def return_keys(self):
        return self.kwargs.keys()

    #  def 
