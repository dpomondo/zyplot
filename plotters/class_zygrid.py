#coumns! /usr/local/bin/python3
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
                                    int: wrap after that many columns (not yet
                                    implemented)
                                    'max': wrap after as many columns
                                    will fit on terminal screen (not yet
                                    implemented)
                                    'columns': if there are multiple `pages`
                                    (i.e. total columns are a multiple of the
                                    number of column names) the iterables will
                                    be wrapped when the column names repeat.
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
                    'padding':
                                Extra width for added to columns. Padding is
                                defined as box_width - minimum_box_width, and
                                updating box_width will also change padding
                                and vice-versa.
                    'column_names_trim_func':
                                function used to trim column names longer
                                than box_width
                    'row_names':    optional row names
                    'box_width':    otherwise box_width will be set as
                                padding plus the minimum box width
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
        self.zyformat['column_widths'] = kwargs.get('column_widths',
                                                    'flexible')
        self.wrap = kwargs.get('wrap', False)
        self.zyformat['color'] = kwargs.get('color', False)
        self.zyformat['title'] = kwargs.get('title', None)
        # both column_names and row_names get routed to functions to set their
        # values
        self.column_names = kwargs.get('column_names', [])
        self.row_names = kwargs.get('row_names', [])
        self.row_flag = kwargs.get('row_flag', True)
        self.row_names_justification = kwargs.get('row_names_justification',
                                                  'center')
        self.column_names_justification = kwargs.get(
            'column_names_justification', 'center')
        self.box_justification = kwargs.get('box_justification', 'center')
        # the following are `magic` for now:
        # and we store the rest for later
        self.padding = kwargs.get('padding', 1)
        #  self.kwargs = kwargs
        self.verbose = False

    def __getattr__(self, attrname):
        if attrname in self.zyformat.keys():
            return self.zyformat[attrname]
        elif attrname in self.__dict__.keys():
            return self.__dict__[attrname]

    #  def __setattr__(self, attrname, value):
        #  object.__setattr__(self, attrname, value)

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
        return "[Zygrid Format Object, <{}> by <{}>]".format(self.width,
                                                             self.length)

    def return_format_dict(self):
        pass

    def zupdate(self, key, value):
        if key in self.zyformat.keys():
            self.zyformat[key] = value

# -----------------------------------------------------------------------------
#
#  Properties
#
# -----------------------------------------------------------------------------

    @property
    def width(self):
        return (len(self.data[0]) if self.row_flag is True else
                len(self.data))

    @property
    def length(self):
        return (len(self.data[0]) if self.row_flag is False else
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
            self._minboxwid = self.min_box_width(self.data, 1)
        return self._minboxwid

    @minimum_box_width.setter
    def minimum_box_width(self, *args):
        self._minboxwid = self.min_box_width(self.data, 1)

    @property
    def box_width(self):
        return self.zyformat.get('box_width', self.minimum_box_width)

    @box_width.setter
    def box_width(self, value):
        value = max(self.minimum_box_width, value)
        self.zyformat['box_width'] = value
        # get a nasty infinite recursion if we use self.padding:
        self.zyformat['padding'] = value - self.minimum_box_width + 1

    @property
    def padding(self):
        if 'padding' not in self.zyformat.keys():
            self.zyformat['padding'] = 1
        return self.zyformat['padding']

    @padding.setter
    def padding(self, value):
        value = max(1, value)
        self.zyformat['padding'] = value
        self.zyformat['box_width'] = self.minimum_box_width + value - 1

    @property
    def row_names(self):
        return self._rnams

    @row_names.setter
    def row_names(self, rws):
        if rws is None or rws == []:
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
        if cols is None or cols == []:
            self._cnams = []
        else:
            if self.width % len(cols) != 0:
                raise ValueError("Number of columns should be a multiple" +
                                 " of number of column names")
            self._cnams = cols[:]

    @property
    def row_flag(self):
        if '_rw_flg' not in self.__dict__.keys():
            self._rw_flg = True
        return self._rw_flg

    @row_flag.setter
    def row_flag(self, value):
        if value not in [True, False]:
            raise AttributeError("row_flag must be True or False")
        # do the setting
        old_val = self._rw_flg
        self._rw_flg = value
        # now the clean-up...
        if old_val != value:
            if len(self.column_names) > 0 or len(self.row_names) > 0:
                _ctemp = self.column_names[:]
                _rtemp = self.row_names[:]
                self.column_names = _rtemp
                self.row_names = _ctemp
                del _ctemp
                del _rtemp
                del old_val

# -----------------------------------------------------------------------------
#  End of Properties
# -----------------------------------------------------------------------------

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
            #  return max(list(len(str(i)) for i in iters))
            biggest = 0
            for it in iters:
                if isinstance(it, list) or isinstance(it, tuple):
                    temp = self.max_list_size(it)
                else:
                    temp = len(str(it))
                if temp > biggest:
                    biggest = temp
            return biggest
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
        if self.verbose:
            print("calculating column widths, setting of {}".format(
                self.zyformat['column_widths']))
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
            # First, how many results do we need(`rnge`) and whether we need to
            # get single columns or multiples 
            if self.wrap == 'columns':
                rnge = len(self.column_names)
                target = lambda x: range(x, self.width, len(self.column_names))
            elif self.wrap is False:
                rnge = self.width
                target = lambda x: range(x, x+1)
            # if 'color' is true, then results will be a 3-tuple, so we need to
            # only take the second item
            if self.zyformat.get('color', False) is False:
                temp_func = lambda x: len(str(x))
            else:
                temp_func = lambda x: len(str(x[1]))
            # we need to slice the data differently depending on whether its
            # rotated or not.
            generator_func = lambda fn, dt: [temp_func(fn(z)) for z in
                                             dt(self.data)]
            if self.row_flag is False:
                gen_tuple = (lambda x: x, lambda z: z[zind])
            else:
                gen_tuple = (lambda x: x[zind], lambda z: z)
            # now we pull the trigger and build the list!
            for i in range(rnge):
                temp_list = []
                for zind in target(i):
                    temp_list += generator_func(*gen_tuple)
                temp = max(temp_list)
                temp_widths.append(temp + padding)
        return temp_widths

    def temp_return_layout(self):
        #  return {'header':   ['title', 'col_names', 'blank'],
        return {'header':   ['title', 'blank'],
                'body':     ['line', 'rows'],
                #  'footer':   ['line']}
                'footer':   ['line', 'col_names']}

    def layout_funcs(self):
        def title(ind, start, stop):
            if self.zyformat.get('title', None) is None:
                return
            if ind != 0:
                return
            if self.wrap is False:
                zemp = self.width
            elif self.wrap == 'columns':
                zemp = len(self.column_names)
            if zemp < stop:
                stop -= len(self.column_names)
            target = sum(self.__col_wid[start:stop])
            if self.row_names != []:
                res = ' ' * (self.max_list_size(
                    self.row_names) + 1)
            else:
                res = ''
            return res + "{:^{wid}}".format(self.zyformat['title'], wid=target)

        def col_names(_, start, stop):
            if self.verbose:
                print("hitting col func...")
            if self.column_names == []:
                return
            if self.column_names_justification == 'right':
                just = '>'
            elif self.column_names_justification == 'left':
                just = '<'
            elif self.column_names_justification == 'center':
                just = '^'
            else:
                raise ValueError("Bad value for column_names_justification:" +
                                 " {}".format(self.column_names_justification))
            if self.wrap is False:
                zemp = self.width
            elif self.wrap == 'columns':
                zemp = len(self.column_names)
            else:
                raise ValueError("{} not a valid value for 'wrap'".format(
                    self.wrap))
            if self.verbose:
                print("survivied the empty name test...")
            col_name_trim_func = self.zyformat.get('col_trim_func',
                lambda x, y: '{:{j}{wid}}'.format(x[0:y], j=just, wid=y))
            res = ' ' * (self.max_list_size(self.row_names) + 1)
            for i in range(start, stop):
                res += col_name_trim_func(
                    self.column_names[i % len(self.column_names)],
                    self.__col_wid[i % zemp])
            return res

        def line(ind, start, stop):
            def make_line():
                # make sure we don't hang if there are no column names
                if len(self.column_names) == 0:
                    temp = self.width
                elif self.wrap == 'columns':
                    temp = len(self.column_names)
                else:
                    temp = self.width
                if self.row_names != []:
                    res = ' ' * (self.max_list_size(
                        self.row_names) + 1)
                else:
                    res = ''
                for i in range(start, stop - 1):
                    res += '+'
                    res += '-' * (self.__col_wid[i % temp] - 1)
                res += '+'
                res += '-' * (self.__col_wid[i % temp] - 2)
                res += '+'
                return res
            lin = None
            targ = []
            # swap the next line with the following four to NOT get a line in
            # between data pages
            targ.append(len(self.row_names))
            # if self.wrap == 'columns':
            #     targ.append(len(self.row_names))
            # else:
            #     targ.append(self.length)
            if any(map(lambda x: ind % x == 0, targ)):
                lin = make_line()
            return lin

        def new_rows(ind, start, stop):
            box_trim_func = self.zyformat.get('box_trim_func',
                                              #  lambda x: str(x))
                                              lambda x: x)
            #  box_format_func = self.return_box_format_func()
            # first we trim & cut the box contents
            if self.box_justification == 'right':
                just = '>'
            elif self.box_justification == 'left':
                just = '<'
            elif self.box_justification == 'center':
                just = '^'
            else:
                raise ValueError("Bad value for box_justification:" +
                                 " {}".format(self.box_justification))
            if self.row_names_justification == 'right':
                rjust = '>'
            elif self.row_names_justification == 'left':
                rjust = '<'
            elif self.row_names_justification == 'center':
                rjust = '^'
            else:
                raise ValueError("Bad value for row_names_justification:" +
                                 " {}".format(self.row_names_justification))
            items = []
            color_mask = []
            for i in range(start, stop):
                if self.row_flag is False:
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
            lines = 1
            for it in items:
                if isinstance(it, list) or isinstance(it, tuple):
                    if len(it) > lines:
                        lines = len(it)
            # now we construnct the strings
            res = []
            for lin in range(lines):
                res.append('')
            if len(self.row_names) > 0:
                rnam_wid = self.max_list_size(self.row_names)
                for lin in range(lines):
                    res[lin] += '{:{rj}{wid}} '.format(
                        self.row_names[ind % len(self.row_names)] if lin ==
                        0 else '',
                        rj=rjust,
                        wid=rnam_wid)
            if len(self.column_names) == 0 or self.wrap is False:
                zemp = self.width
            else:
                zemp = len(self.column_names)
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
                    res[lin] += "{}{:{j}{wid}}{}".format(
                        color_mask[it],
                        zitm,
                        '\033[0m',
                        j=just,
                        wid=self.__col_wid[it % zemp])
            return res

        def blank(_, start, stop):
            res = ' ' * self.max_list_size(self.row_names)
            for i in range(start, stop):
                if len(self.column_names) == 0:
                    temp = self.width
                else:
                    temp = len(self.column_names)
                res += ' ' * self.__col_wid[i % temp]
            return res

        _dic = {'col_names':    col_names,
                'title':        title,
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
                if self.row_flag is True:
                    z, y = i, j
                else:
                    y, z = i, j
                res[-1] += '{:{wid}}'.format(self.data[z][y],
                                             wid=self.__col_wid[j])
        for lin in res:
            print(lin)

    def layout_parser(self, begin_offset=0, end_offset=0,
                      row_offset=0, last_row_offset=0):
        """ Return a list of formatting functions for use on self.data.  """
        self.__col_wid = self.get_column_widths()
        layout = self.temp_return_layout()
        layout_func_dic = self.layout_funcs()
        layout_stack = []

        if self.wrap == 'columns':
            jump = len(self.column_names)
        else:
            jump = self.width
        begin = 0
        end = self.width
        for frm in layout['header']:
            ind = 0
            layout_stack.append((layout_func_dic[frm],
                                 (ind, begin + begin_offset,
                                 min(begin + jump - end_offset,
                                     end))))
        while begin < end:
            for ind in range(row_offset, self.length - last_row_offset):
                for frm in layout['body']:
                    layout_stack.append((layout_func_dic[frm],
                                         (ind, begin + begin_offset,
                                         min(begin + jump - end_offset,
                                             end))))
            begin += jump
        for frm in layout['footer']:
            ind = self.length
            layout_stack.append((layout_func_dic[frm],
                                 (ind, begin_offset,
                                 min(jump - end_offset, end))))
        return layout_stack

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
        funcs = self.layout_parser(begin_offset=begin,
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
