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
        self.title = kwargs.get('title', None)
        # both column_names and row_names get routed to functions to set their
        # values
        self.column_names = kwargs.get('column_names', [])
        self.row_names = kwargs.get('row_names', [])
        self.row_flag = kwargs.get('row_flag', True)
        self.row_names_justification = kwargs.get('row_names_justification',
                                                  'right')
        self.column_names_justification = kwargs.get(
            'column_names_justification', 'center')
        self.box_justification = kwargs.get('box_justification', 'left')
        self.zyformat['row_trim_func'] = kwargs.get('row_trim_func',
            lambda x: x)
        self.zyformat['col_trim_func'] = kwargs.get('col_trim_func',
            lambda x: x)
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
        else:
            raise AttributeError

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
        #  if self.zyformat.get('column_names', None) is None:
        if self.column_names == []:
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
            # swap column names and row names
            if len(self.column_names) > 0 or len(self.row_names) > 0:
                _ctemp = self.column_names[:]
                _rtemp = self.row_names[:]
                self.column_names = _rtemp
                self.row_names = _ctemp
            # swap trim funcs
            _ctemp = self.zyformat['col_trim_func']
            _rtemp = self.zyformat['row_trim_func']
            self.zyformat['row_trim_func'] = _ctemp
            self.zyformat['col_trim_func'] = _rtemp
            del _ctemp
            del _rtemp
        del old_val

# -----------------------------------------------------------------------------
#  End of Properties
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#   Helper Functions
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

    def return_justification(self, form):
        if form == 'right':
            return '>'
        elif form == 'left':
            return '<'
        elif form == 'center':
            return '^'
        else:
            raise ValueError("Bad value: {} ".format(form))


# -----------------------------------------------------------------------------
#   End of Helper Functions
# -----------------------------------------------------------------------------

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
                if self.column_names == []:
                    rnge = self.width
                    target_skip = self.width
                else:
                    rnge = len(self.column_names)
                    target_skip = len(self.column_names)
                target = lambda x: range(x, self.width, target_skip)
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
            # now pull the trigger and build the list!
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
                #  'body':     ['rows'],
                #  'footer':   ['line']}
                'footer':   ['line', 'col_names']}

    def layout_funcs(self):
        def title(ind, start, stop):
            #  if self.zyformat.get('title', None) is None:
            if self.title is None:
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
            return res + "{:^{wid}}".format(self.title, wid=target)

        def col_names(_, start, stop):
            if self.column_names == []:
                return
            #  just = self.return_justification(self.column_names_justification)
            if self.wrap is False:
                zemp = self.width
            elif self.wrap == 'columns':
                zemp = len(self.column_names)
            else:
                raise ValueError("{} not a valid value for 'wrap'".format(
                    self.wrap))
            #  col_name_trim_func = self.zyformat.get('col_trim_func',
                #  lambda x, y: '{:{j}{wid}}'.format(x[0:y], j=just, wid=y))
            if hasattr(self, 'row_name_width'):
                res = ' ' * (self.row_name_width + 1)
            else:
                # this returns an empty string if self.row_names == []
                res = ' ' * (self.max_list_size(self.row_names) + 1)
            for i in range(start, stop):
                _wid=self.__col_wid[i % zemp]
                #  res += col_name_trim_func(
                res += '{:{j}{wid}}'.format(
                    self.zyformat['col_trim_func'](
                        self.column_names[i % len(self.column_names)])[:_wid],
                    j=self.return_justification(
                        self.column_names_justification),
                    wid=_wid)
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
                    if hasattr(self, 'row_name_width'):
                        res = ' ' * (self.row_name_width + 1)
                    else:
                        res = ' ' * (self.max_list_size(self.row_names) + 1)
                else:
                    res = ''
                for i in range(start, stop - 1):
                    res += '+'
                    res += '-' * (self.__col_wid[i % temp] - 1)
                res += '+'
                res += '-' * (self.__col_wid[(stop - 1) % temp] - 2)
                res += '+'
                return res
            lin = None
            targ = []
            # swap the next line with the following four to NOT get a line in
            # between data pages
            if self.row_names != []:
                targ.append(len(self.row_names))
            else:
                targ.append(self.length)
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
            #  just = self.return_justification(self.box_justification)
            #  rjust = self.return_justification(self.row_names_justification)
            items = []
            color_mask = []

            target_slice = self.__getitem__(ind)
            for thing in target_slice[start:stop]:
            #  for thing in self.__getitem__(ind)[start:stop]:
                if self.zyformat.get('color', False) is False:
                    itm = thing
                    color = ''
                else:
                    itm = thing[1]
                    color = thing[0]
                #  items.append(box_trim_func(self.data[zzz][vvv]))
                items.append(box_trim_func(itm))
                color_mask.append(color)
            # Dealing with multi-line boxes
            lines = 1
            for it in items:
                if isinstance(it, list) or isinstance(it, tuple):
                    if len(it) > lines:
                        lines = len(it)
            # now we construnct the strings
            res = []
            for lin in range(lines):
                res.append('')
            #  row_name_trim_func = self.zyformat.get('row_trim_func',
                #  lambda x, y: '{:{j}{wid}}'.format(x[0:y], j=rjust, wid=y))
            if len(self.row_names) > 0:
                if hasattr(self, 'row_name_width'):
                    rnam_wid = self.row_name_width
                else:
                    rnam_wid = self.max_list_size(self.row_names)
                assert isinstance(rnam_wid, int)
                assert rnam_wid > 0
                for lin in range(lines):
                    #  res[lin] += row_name_trim_func(
                    res[lin] += '{:{j}{wid}}'.format(
                        self.zyformat['row_trim_func'](
                            self.row_names[ind % len(self.row_names)] if lin ==
                            0 else '')[:rnam_wid],
                        j=self.return_justification(
                            self.row_names_justification),
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
                    elif isinstance(items[it], list) and lin < len(items[it]):
                        zitm = items[it][lin]
                    elif isinstance(items[it], tuple) and lin < len(items[it]):
                        zitm = items[it][lin]
                    # this line should ONLY be hit if items[it] is a singleton
                    # type (str, int, float, etc) and so should go on the first
                    # line. In theory it SHOULD be equivalent to the
                    # commented-out line that follows, but more general
                    elif lin == 0:
                    #  elif isinstance(items[it], str) and lin == 0:
                        zitm = items[it]
                    #  res[lin] += '{:^{wid}}'.format(
                    pad = 1 + (self.padding - 1) // 2
                    res[lin] += "{}{}{:{j}{wid}}{}".format(
                        color_mask[it],
                        ' ' * pad,
                        zitm,
                        '\033[0m',
                        j=self.return_justification(self.box_justification),
                        #  j=just,
                        wid=self.__col_wid[it % zemp] - pad)
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
                #  'rows':         new_new_rows,
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

        begin = 0
        end = self.width
        if self.wrap == 'columns':
            if self.column_names == []:
                jump = self.width
            else:
                jump = len(self.column_names)
            target = self.length
        else:
            # # option one...
            jump = self.width
            target = self.length
            # # option 2...
            #  if self.row_flag is True:
                #  jump = self.width
                #  target = self.length
            #  else:
                #  jump = self.length
                #  target = self.width
            # # option 3
            #  jump = max(self.width, self.length)
            #  target = min(self.width, self.length)
        for frm in layout['header']:
            ind = 0
            layout_stack.append((layout_func_dic[frm],
                                 (ind, begin + begin_offset,
                                 min(begin + jump - end_offset,
                                     end))))
        while begin < end:
            for ind in range(row_offset, target - last_row_offset):
                for frm in layout['body']:
                    layout_stack.append((layout_func_dic[frm],
                                         (ind, begin + begin_offset,
                                         min(begin + jump - end_offset,
                                             end))))
            begin += jump
            if begin > self.width * 2:
                print("help me! I'ma looping! begin:{} jump:{}".format(begin,
                                                                       jump))
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


def zygrid_test(grid, col_wids=False):
    thunder = [(True, False),
               (True, 'columns'),
               (False, False),
               (False, 'columns')]
    temp_title = grid.title
    temp_wrap = grid.wrap
    temp_row_flag = grid.row_flag
    if col_wids is True:
        temp = grid.column_names
        working = []
        for ind in range(len(grid.column_names)):
            working.append("{}: {}".format(ind, grid._Zygrid__col_wid[ind]))
        grid.column_names = working
    for tup in thunder:
        try:
            print('-' * 79)
            print()
            grid.row_flag = tup[0]
            grid.wrap = tup[1]
            grid.title = "row_flag: {} wrap: {}".format(grid.row_flag,
                                                        grid.wrap)
            grid.title += " wid: {} len: {}".format(grid.width,
                                                    grid.length)
            grid.show()
            print()
        except Exception as e:
            print("Caught exception: {}".format(e))
            print("Current... row_flag: {} wrap: {}".format(grid.row_flag,
                                                            grid.wrap))
    grid.row_flag = temp_row_flag
    grid.wrap = temp_wrap
    grid.title = temp_title
    if col_wids is True:
        grid.column_names = temp


def randword(s, e):
    import random
    import string

    return ''.join(random.sample(string.ascii_lowercase,
                                 random.randint(s, e)))


def color_maker(clear=False):
    if clear is False:
        import random
        return "\033[38;5;{}m\033[48;5;{}m".format(random.randint(0, 255),
                                                   random.randint(0, 255))
    else:
        return '\033[0m'


def random_table_test(cols=6, rows=3, box=(3, 7), cnams=7, rnams=7, color=False):
    clear = color_maker(clear=True)
    working = []
    for i in range(rows):
        working.append([])
        for j in range(cols):
            if color is False:
                working[-1].append(randword(box[0], box[1]))
            else:
                working[-1].append((color_maker(), 
                                    randword(box[0], box[1]),
                                    clear))

    colnams, rownams = [], []
    for i in range(cols):
        colnams.append(randword(1, cnams))
    for j in range(rows):
        rownams.append(randword(1, rnams))

    return working, colnams, rownams


def ordered_table_test(cols=6, rows=3, box=3, cnams=3, rnams=3, color=False):
    import string
    working = []
    for i in range(rows):
        working.append([])
        for j in range(cols):
            if color is False:
                working[-1].append(string.ascii_letters[(i * cols) + j] * box)
            else:
                working.append((color_maker(),
                                string.ascii_letters[(i * cols) + j] * box,
                                color_maker(clear=True)))

    colnams, rownams = [], []
    for i in range(cols):
        colnams.append(str(i) * cnams)
    for j in range(rows):
        rownams.append(str(j) * rnams)

    return working, colnams, rownams
