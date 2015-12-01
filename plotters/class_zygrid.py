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


# TODO rename this to Zytable since grid is dumb and it SHOULD be a table
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
                                Default is 'flexible'.
                                Options:
                                    'equal': uses smallest width that
                                    fits the largest item for all columns.
                                    'flexible': each column is as wide as
                                    needed to fit the largest item.
                                    integer: each coumn will be the largest
                                    of either the value of 'equal' or the
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
        self.zyformat = {}
        # mebbe 'rows' as kwarg for 'row_flag' is a bad idea...
        self.zyformat['row_flag'] = kwargs.get('row_flag', True)
        self.zyformat['column_widths'] = kwargs.get('column_widths',
                                                    'flexible')
        self.zyformat['wrap'] = kwargs.get('wrap', None)
        self.zyformat['color'] = kwargs.get('color', False)
        # both column_names and row_names get routed to functions to set their
        # values
        self.column_names = kwargs.get('column_names', None)
        self.row_names = kwargs.get('row_names', None)
        # the following are `magic` for now:
        #  self.wrap = False
        # and we store the rest for later
        self.zyformat['padding'] = kwargs.get('padding', 1)
        #  self.kwargs = kwargs
        self.verbose = False

    def __getattr__(self, attrname):
        if attrname in self.zyformat.keys():
            return self.zyformat[attrname]
        elif attrname in self.__dict__.keys():
            return self.__dict__[attrname]

    def __setattr__(self, attrname, value):
        #  if attrname == 'column_names':
            #  self.set_column_names(value)
        if attrname == 'padding':
            value = max(1, value)
            object.__setattr__(self, attrname, value)
        elif attrname == 'row_flag':
            if value not in (True, False):
                raise ValueError(value)
            if value != self.__dict__.get('row_flag', True):
                object.__setattr__(self, attrname, value)
                if len(self.column_names) > 0:
                    temp = self.column_names
                    self.column_names = self.row_names
                    self.row_names = temp
            else:
                object.__setattr__(self, attrname, value)
        else:
            object.__setattr__(self, attrname, value)

    def __len__(self):
        if self.zyformat['row_flag'] is False:
            return len(self.data[0])
        else:
            return len(self.data)

    def __getitem__(self, ind):
        if self.zyformat['row_flag'] is True:
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

    def return_format_dict(self):
        pass

    def zupdate(self, key, value):
        if key in self.zyformat.keys():
            self.zyformat[key] = value

    @property
    def width(self):
        return (len(self.data[0]) if self.zyformat['row_flag'] is True else
                len(self.data))

    @property
    def length(self):
        return (len(self.data[0]) if self.zyformat['row_flag'] is False else
                len(self.data))

    @property
    def depth(self):
        """ Return how many columns each column name refers to.
        """
        if self.zyformat.get('column_names', None) is None:
            return 1
        else:
            return int(self.width / len(self.column_names))

    @property
    def minimum_box_width(self):
        if '_minboxwid' not in self.__dict__.keys():
            self._minboxwid = self.min_box_width(self.data, self.padding)
        return self._minboxwid

    @minimum_box_width.setter
    def minimum_box_width(self, *args):
        self._minboxwid = self.min_box_width(self.data, self.padding)

    @property
    def box_width(self):
        return self.zyformat.get('box_width', self.minimum_box_width)

    @box_width.setter
    def box_width(self, value):
        self.zyformat['box_width'] = max(self.minimum_box_width, value)

    @property
    def row_names(self):
        return self._rnams

    @row_names.setter
    def row_names(self, rws):
        if rws is None:
            self._rnams = []
        else:
            if self.length % len(rws) != 0:
                raise ValueError("Number of rows should be a multiple" +
                                 " of number of row names")
            self._rnams = rws[:]

    @property
    def column_names(self):
        return self._cnams

    @column_names.setter
    def column_names(self, cols):
        if cols is None:
            self._cnams = []
        else:
            if self.width % len(cols) != 0:
                raise ValueError("Number of columns should be a multiple" +
                                 " of number of column names")
            self._cnams = cols[:]

    def return_box_format_func(self):
        if self.zyformat.get('color', False) is not False:
            return lambda x, y: "{}{:^{wid}}{}".format(*x, wid=y)
        else:
            return lambda x, y: "{:^{wid}}".format(str(x), wid=y)

    def min_list_size(self, iters):
        if len(iters) > 0:
            return min(list(len(str(i)) for i in iters))
        else:
            return 0

    def max_list_size(self, iters):
        if len(iters) > 0:
            return max(list(len(str(i)) for i in iters))
        else:
            return 0

    def min_box_width(self, iters, padding=0):
        temp_box_width = 0
        if self.zyformat.get('color', False) is False:
            for it in iters:
                temp_box_width = max(temp_box_width, self.max_list_size(it))
        else:
            # each object it in iters should be a 3-tuple, with a color
            # code as 0, the table entry as 1, and a color clear code as 2
            for it in iters:
                temp_box_width = max(temp_box_width,
                                     self.max_list_size(
                                         list(i[1] for i in it)))
        return temp_box_width + padding

    def get_column_widths(self):
        """ Create a list of ints for use in formatting columns.    """
        if ('column_widths' not in self.zyformat.keys()):
            self.zyformat['column_widths'] = self.kwargs.get('column_widths',
                                                             'flexible')
        temp_widths = []
        padding = max(1, self.zyformat['padding'])
        if self.zyformat['column_widths'] == 'equal':
            for i in range(self.width):
                temp_widths.append(self.box_width)
        elif isinstance(self.zyformat['column_widths'], int):
            # here we need to integrate self.box_width properly...
            temp = max(self.box_width, self.zyformat['column_widths'])
            for i in range(self.width):
                temp_widths.append(temp)
        elif self.zyformat['column_widths'] == 'columns':
            if self.column_names is None:
                # this is a terrible solution and must be fixed...
                # A proper solution shouln't change a passed-in attribute
                self.zyformat['column_widths'] = 'flexible'
            else:
                for nam in self.column_names:
                    temp_widths.append(max(self.minimum_box_width,
                                           len(nam) + padding))
        elif self.zyformat['column_widths'] == 'flexible':
            if self.zyformat['row_flag'] is False:
                for i in range(self.width):
                    temp_widths.append(
                        max(len(str(zit)) for zit in self.data[i]) +
                        padding)
            else:
                for i in range(self.width):
                    temp_widths.append(
                        max(len(str(zit[i])) for zit in self.data) +
                        padding)
        return temp_widths

    def temp_return_format(self):
        return {'header':   ['col_names', 'blank'],
                'body':     ['line', 'rows'],
                'footer':   ['line']}

    def formatting_funcs(self):
        def col_names(_, start, stop):
            col_name_trim_func = self.zyformat.get('col_trim_func',
                lambda x, y: '{:^{wid}}'.format(x[0:y], wid=y))
            res = ' ' * (self.max_list_size(self.row_names) + 1)
            for i in range(start, stop):
                res += col_name_trim_func(
                    self.column_names[i % len(self.column_names)],
                    self.__col_wid[i % len(self.column_names)])
            return res

        def line(ind, start, stop):
            def make_line():
                res = ' ' * (self.max_list_size(
                    self.row_names) + 1)
                for i in range(start, stop - 1):
                    res += '+'
                    res += '-' * (self.__col_wid[i % len(
                        self.column_names)] - 1)
                res += '+'
                res += '-' * (self.__col_wid[i % len(
                    self.column_names)] - 2)
                res += '+'
                return res
            temp = None
            if ind % self.length == 0:
                temp = make_line()
            return temp

        def new_rows(ind, start, stop):
            box_trim_func = self.zyformat.get('box_trim_func',
                                              lambda x: str(x))
            #  box_format_func = self.return_box_format_func()
            # first we trim & cut the box contents
            items = []
            color_mask = []
            for i in range(start, stop):
                if self.zyformat['row_flag'] is False:
                    zzz, vvv = i, ind
                else:
                    zzz, vvv = ind, i
                if self.zyformat.get('color', False) is False:
                    itm = self.data[zzz][vvv]
                    color = ''
                else:
                    itm = self.data[zzz][vvv][1]
                    color = self.data[zzz][vvv][0]
                #  items.append(box_trim_func(self.data[zzz][vvv]))
                items.append(box_trim_func(itm))
                color_mask.append(color)
            if self.verbose:
                print("items to be formatted\n\t", items)
            lines = 1
            for it in items:
                if isinstance(it, list) or isinstance(it, tuple):
                    if len(it) > lines:
                        lines = len(it)
            if self.verbose:
                print("lines: ", lines)
            # now we construnct the strings
            res = []
            for lin in range(lines):
                res.append('')
            if self.verbose:
                print('res so far:\n\t', res)
            if len(self.row_names) > 0:
                rnam_wid = self.max_list_size(self.row_names)
                for lin in range(lines):
                    res[lin] += '{:<{wid}} '.format(
                        self.row_names[ind % len(self.row_names)] if lin ==
                        0 else '',
                        wid=rnam_wid)
            if self.verbose:
                print('res so far:\n\t', res)
            for lin in range(lines):
                for it in range(len(items)):
                    zitm = ''
                    if lines == 1:
                        zitm = items[it]
                    # the following line is a bug waiting to happen (if the
                    # `items` list consists of ints or floats, for example)
                    # Possible fix: require box_trim_func to return either
                    # a list of strings or a string
                    elif isinstance(items[it], str) and lin == 0:
                        zitm = items[it]
                    elif isinstance(items[it], list) and lin < len(items[it]):
                        zitm = items[it][lin]
                    elif isinstance(items[it], tuple) and lin < len(items[it]):
                        zitm = items[it][lin]
                    #  res[lin] += '{:^{wid}}'.format(
                    res[lin] += "{}{:^{wid}}{}".format(
                        color_mask[it],
                        zitm,
                        '\033[0m',
                        wid=self.__col_wid[it % len(self.column_names)])
                    if self.verbose:
                        print("length of res:\n\t", len(res[lin]), res[lin])
            return res

        def rows(ind, start, stop):
            res = ''
            if len(self.row_names) > 0:
                res += '{:<{wid}} '.format(
                    self.row_names[ind % len(self.row_names)],
                    wid=self.max_list_size(self.row_names))
            for i in range(start, stop):
                if self.zyformat['row_flag'] is False:
                    zzz, vvv = i, ind
                else:
                    zzz, vvv = ind, i
                res += '{:^{wid}}'.format(
                    self.data[zzz][vvv],
                    wid=self.__col_wid[i % len(self.column_names)])
            thunder = []
            thunder.append(res)
            return thunder

        def blank(_, start, stop):
            res = ' ' * self.max_list_size(self.row_names)
            for i in range(start, stop):
                res += ' ' * self.__col_wid[i % len(self.column_names)]
            return res

        _dic = {'col_names':    col_names,
                'line':         line,
                #  'rows':         rows,
                'rows':         new_rows,
                'blank':        blank}
        return _dic

    def return_keys(self):
        return self.kwargs.keys()

    def pprinter(self):
        #  set it each time columns_widths gets set...
        self.__col_wid = self.get_column_widths()
        res = []
        for i in range(self.length):
            res.append('')
            for j in range(self.width):
                if self.zyformat['row_flag'] is True:
                    z, y = i, j
                else:
                    y, z = i, j
                res[-1] += '{:{wid}}'.format(self.data[z][y],
                                             wid=self.__col_wid[j])
        for lin in res:
            print(lin)

    # TODO rename this and associated yabberdy yab to `layout` and
    # `layout_parser` so there is less confusion with the stuff in zyformat
    def format_parser(self, begin_offset=0, end_offset=0,
                      row_offset=0, last_row_offset=0):
        """ Return a list of formatting functions for use on self.data.  """
        self.__col_wid = self.get_column_widths()
        formatter = self.temp_return_format()
        format_func_dic = self.formatting_funcs()
        formatters_list = []
        # hacktastic defaults for now...
        if self.zyformat.get('wrap', False) == 'columns':
            jump = len(self.column_names)
        else:
            jump = self.width
        begin = 0
        end = self.width
        for frm in formatter['header']:
            ind = 0
            formatters_list.append((format_func_dic[frm],
                                   (ind, begin + begin_offset,
                                   min(begin + jump - end_offset,
                                       end))))
        while begin < end:
            for ind in range(row_offset, self.length - last_row_offset):
                for frm in formatter['body']:
                    formatters_list.append((format_func_dic[frm],
                                            (ind, begin + begin_offset,
                                            min(begin + jump - end_offset,
                                                end))))
            begin += jump
        for frm in formatter['footer']:
            ind = self.length
            formatters_list.append((format_func_dic[frm],
                                   (ind, begin_offset,
                                   min(jump - end_offset, end))))
        return formatters_list

    def show(self, *args, **kwargs):
        if len(args) > 4:
            raise KeyError
        begin = args[0] if len(args) > 0 else 0
        end = args[1] if len(args) > 1 else 0
        row_offset = args[2] if len(args) > 2 else 0
        last_row_offset = args[3] if len(args) > 3 else 0
        # TODO: find a way to call method while only temporarily changing
        # settings
        for key in kwargs:
            self.zupdate(key, kwargs[key])
        funcs = self.format_parser(begin_offset=begin,
                                   end_offset=end,
                                   row_offset=row_offset,
                                   last_row_offset=last_row_offset)
        res = []
        for fn in funcs:
            if self.verbose > 1:
                print("function: {}\t args: {}, {}, {}".format(fn[0], *fn[1]))
            temp = fn[0](*fn[1])
            if temp is not None:
                if isinstance(temp, str):
                    res.append(temp)
                if isinstance(temp, list):
                    res.extend(temp)
        for lin in res:
                print(lin)
