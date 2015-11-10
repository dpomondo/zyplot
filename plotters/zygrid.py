#! /usr/local/bin/python3
# coding=utf-8
#
# -----------------------------------------------------------------------------
#   file:       zygrid.py
#   use:
#
#   author:     dpomondo
#   site:       github.com/dpomondo/zyplot
# -----------------------------------------------------------------------------

home_dir = '/usr/self/bin/zyplot'
import sys
if home_dir not in sys.path:
    sys.path.append(home_dir)
import utils.zyutils as zyutils


def row_names_generator(row_names=None):
    """ Takes a list or None, returns tuple including a width and a generator.

        If a list of names is passed in as row_names, this returns the width of
        the formatted names as well as a generator function that yields
        formatted versions of those names.

        If instead `None` is passed in, the width is returned as 0 and the
        generator function returns an endless sequence of the empty string.

        This was done so that the `row_names is None` test could be done only
        once, instead of each time through the loop over the iterables list.
        """
    if row_names is None:
        def yielder():
            while True:
                yield ''
        return 0, yielder()
    else:
        width = max(list(len(x) for x in row_names if x is not None))

        def yielder():
            nams = row_names
            #  while nams:
                #  yield "{:>{wid}}: ".format(nams[0], wid=width)
                #  #  yield row_names[0]
                #  nams = nams[1:]
            zindex = 0
            len_nams = len(nams)
            while True:
                yield "{:>{wid}}: ".format(nams[zindex % len_nams],
                                           wid=width)
                zindex += 1

        return width + 2, yielder()


def row_content_generator(iterables, format_func, rows=True):
    if rows is False:
        ind = range(len(iterables[0]))
        #  temp = ''.join(list(format_func(it[i]) for it in iterables))

        def yielder():
            for i in ind:
                yield ''.join(list(format_func(it[i]) for it in iterables))
        return yielder()
    else:
        ind = range(len(iterables))

        def yielder():
            for i in ind:
                yield ''.join(list(format_func(it) for it in iterables[i]))
        return yielder()


def min_box_width(iterables, buffer=0, color=False):
        box_width = 0
        if color is False:
            for it in iterables:
                for i in it:
                    if len(str(i)) > box_width:
                        box_width = len(str(i))
        else:
            # each object it in iterables should be a 3-tuple, with a color
            # code as 0, the table entry as 1, and a color clear code as 2
            for it in iterables:
                for i in it:
                    if len(str(i[1])) > box_width:
                        box_width = len(str(i[1]))
        return box_width + buffer


def max_box_width(num_boxes, name_width=0, padding=0):
    screen_width = zyutils.get_terminal_width()
    total_boxes_width = screen_width - name_width - (2 * padding)
    print("Screen is {} wide, fitting {} boxes".format(screen_width,
                                                       num_boxes))
    return total_boxes_width // num_boxes



def wrap_iterables(iterables, screen_width, minimum_box_width,
        row_name_width, rows, wrap_target, color_flag):
    """ yarg
        """
    #  if rows is False:
        #  num_rows = len(iterables[0])
        #  num_boxes = len(iterables)
    #  else:
    num_rows = len(iterables)
    num_boxes = len(iterables[0])

    verbose = True
    if verbose:
        print("Wrapping columns... ", end='')
    working_width = screen_width - row_name_width
    if wrap_target == 'max':
        if row_name_width + (num_boxes * minimum_box_width) <= screen_width:
            if verbose:
                print("Max columns fit!")
            return iterables
        else:
            new_num_boxes = working_width // minimum_box_width
    else:
        new_num_boxes = int(wrap_target)
    if new_num_boxes >= num_boxes:
        if verbose:
            print("column wrapping set higher than number of columns...")
        return iterables

    # do the wrapping!
    if verbose:
        print("New number of columns: {}".format(new_num_boxes))
    res = []
    if rows is True:
        even_cols = len(iterables[0]) // new_num_boxes
        residue = len(iterables[0]) % new_num_boxes
        for ind in range(even_cols):
            for jin in range(num_rows):
                res.append(iterables[jin][ind * new_num_boxes : (ind + 1)
                                          * new_num_boxes])
        if residue > 0:
            for zin in range(num_rows):
                temp = iterables[zin][-residue:]
                for z in range(new_num_boxes - residue):
                    temp.append('' if color_flag is False else ('', '', ''))
                res.append(temp)
        return res
    else:
        raise NotImplementedError


def rotate_iterables(iterables):
    res = []
    for i in range(len(iterables[0])):
        res.append([])

    for ziter in iterables:
        for ind in range(len(ziter)):
            res[ind].append(ziter[ind])

    return res


def zygrid(*iterables, **kwargs):
    """ Takes lists, returns them formatted as a printable table.

        *iterables:     Multiple same-length lists or tuples. These can be
                        either rows or columns depending on whether the 'row'
                        arg in kwargs is True or False.
        *kwargs:        Formatting args, passed in as a dictionary. Options
                        include:
                        True/False options:
                        'rows':     whether *iterables are to be formatted as
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
                        'column_names_trim_func':
                                    function used to trim column names longer
                                    than box_width
                        'row_names':    optional row names
                        'box_width':    otherwise box_width will be set as
                                    a function of the widest item
                        'side_padding': buffer of blank spaces to the right and
                                    left of the formatted table
                        'table_justification':
                                    'right': table formatted to right margin
                                    'center': table centered
                                    'left' or None: formatted to left margin
        """

    # set up the crucial variables
    rows = kwargs.get('rows', True)
    row_name_width, row_name_iterator = row_names_generator(
        kwargs.get('row_names', None))
    
    # next, massage & measure the iterables
    if rows is False:
        iterables = rotate_iterables(iterables)
        rows = True

    # are we wrapping the rows:
    wrap_flag = kwargs.get('wrap', False)
    screen_width = zyutils.get_terminal_width()
    minimum_box_width = min_box_width(iterables,
                                      buffer=kwargs.get('box_buffer', 1),
                                      color=kwargs.get('color', False))
    if wrap_flag is not False:
        iterables = wrap_iterables(iterables, screen_width, minimum_box_width,
                                   row_name_width, rows, wrap_flag, 
                                   kwargs.get('color', False))

    num_rows = len(iterables)
    num_boxes = len(iterables[0])
    # deal with color vs. no color
    if kwargs.get('color', None) is not None:
        format_func = lambda x: "{}{:^{wid}}{}".format(*x, wid=box_width)
    else:
        format_func = lambda x: "{:^{wid}}".format(str(x), wid=box_width)

    # set up the row contents
    row_content_iterator = row_content_generator(iterables, format_func, rows)

    # get the width of the boxes
    if kwargs.get('box_width', None) == 'max':
        box_width = max_box_width(num_boxes=num_boxes,
                                  name_width=row_name_width,
                                  padding=kwargs.get('side_padding', 0))
    elif kwargs.get('box_width', None) is not None:
        box_width = kwargs['box_width']
    else:
        box_width = minimum_box_width
        #  box_width = min_box_width(iterables,
                                  #  buffer=kwargs.get('box_buffer', 1),
                                  #  color=kwargs.get('color', False))
    box_width = max(box_width, minimum_box_width)
    width_residual = screen_width - (num_boxes * box_width) - row_name_width

    # justification for table
    if kwargs.get('table_justification', None) == 'right':
        right_pad = ' ' * width_residual
    elif kwargs.get('table_justification', None) == 'center':
        right_pad = ' ' * (width_residual // 2)
    else:
        if kwargs.get('side_padding', 0) > 0:
            right_pad = ' ' * kwargs['side_padding']
        else:
            right_pad = ''

    # prepare the column names
    if kwargs.get('column_names', None) is not None:
        #  column_names = kwargs['column_names']
        column_names = ' ' * row_name_width
        if kwargs.get('column_names_trim_func', None) is None:
            for nam in kwargs['column_names']:
                column_names += '{:^{wid}}'.format(nam if len(nam) < box_width
                                                   else nam[:box_width - 4]
                                                   + '...',
                                                   wid=box_width)
        else:
            for nam in kwargs['column_names']:
                column_names += '{:^{wid}}'.format(
                    nam if len(nam) < box_width else
                    kwargs['column_names_trim_func'](nam)[:box_width],
                    wid=box_width)
        column_names = right_pad + column_names
    else:
        column_names = None

    # make the strings!
    res = []

    for i in range(num_rows):
        r_nam = next(row_name_iterator)
        temp = next(row_content_iterator)
        res.append(right_pad + r_nam + temp)

    if column_names is not None:
        res.insert(0, column_names)
    return res


def main():
    import random
    import string
    # test number one...
    test1 = []
    for i in range(11):
        test1.append(random.sample(range(100000) if random.random() > 0.5
                                   else range(1000),
                                   10))
    rw_nams, col_names = [], []
    for i in range(len(test1)):
        rw_nams.append(''.join(random.sample(string.ascii_lowercase,
                                             random.randint(1, 10))))
    for i in range(len(test1[0])):
        col_names.append(''.join(random.sample(string.ascii_lowercase,
                                               random.randint(2, 20))))

    frmt_dic = {'column_names': col_names,
                'box_width': 10,
                'row_names': rw_nams,
                'table_justification': 'center'}

    res = zygrid(*test1, **frmt_dic)
    print("Testing 10x10 centered grid {} lines long".format(len(res)))
    for lin in res:
        print(lin)

    print("\nTesting same, but with bow_width set to 'max'," +
          " table_justification set to 'right', and trim function")
    frmt_dic['column_names_trim_func'] = lambda x: '<short>'
    frmt_dic['box_width'] = 'max'
    frmt_dic['table_justification'] = 'right'
    res = zygrid(*test1, **frmt_dic)
    for lin in res:
        print(lin)

    # test number two, includes row = False
    test2 = []
    for i in range(5):
        test2.append(random.sample(range(1000), 5))

    frmt_dic2 = {'rows':    False
                 }

    print("\nTest 2, {} columns with {} rows, 'rows' set to {}".format(
        len(test2),
        len(test2[0]),
        frmt_dic2['rows']))
    res = zygrid(*test2, **frmt_dic2)
    for lin in res:
        print(lin)

    print("\nSame table, but with 'rows' set to default (True)")
    res2 = zygrid(*test2)
    for lin in res2:
        print(lin)

    frmt_dic2['side_padding'] = 5
    print("Side Padding set to {}".format(frmt_dic2['side_padding']))
    res3 = zygrid(*test2, **frmt_dic2)
    for lin in res3:
        print(lin)

    # third test... colors!
    print("\nTesting color formatting & tuple unpacking...")
    test3 = []
    clear = '\033[0m'

    def color_maker():
        return "\033[38;5;{}m\033[48;5;{}m".format(random.randint(0, 255),
                                                   random.randint(0, 255))
    for i in range(8):
        test3.append([])
        for j in range(10):
            test3[i].append((color_maker(), random.randint(0, 100000), clear))
    rw_nams = []
    for i in range(len(test3)):
        rw_nams.append(''.join(random.sample(string.ascii_lowercase,
                                             random.randint(1, 10))))
    frmt_dic3 = {'color':    True,
                 'row_names': rw_nams}

    res = zygrid(*test3, **frmt_dic3)
    for lin in res:
        print(lin)
    frmt_dic3['box_width'] = 'max'
    frmt_dic3['table_justification'] = 'center'
    res = zygrid(*test3, **frmt_dic3)
    print("\nSame, but with box_width set to 'max' and cenetered")
    for lin in res:
        print(lin)

    frmt_dic3['side_padding'] = 0
    frmt_dic3['box_width'] = 2
    print("\nIterating through different wrap settings...")
    for i in range(2,14):
        frmt_dic3['wrap'] = i
        res = zygrid(*test3, **frmt_dic3)
        print("Wrap set to {}".format(frmt_dic3['wrap']))
        for lin in res:
            print(lin)


if __name__ == '__main__':
    main()
