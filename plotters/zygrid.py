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
                        'wrap':     whether or not rows are wrapped after
                                    a certain length.

                        Options with arguments:
                        'column_names':
                                        optional column names
                        'row_names':    optional row names
                        'box_width':    otherwise box_width will be set as
                                    a function of the widest item
        """

    # set up the crucial variables
    if kwargs.get('row_names', None) is not None:
        row_names = kwargs['row_names']
        row_name_width = max(list(
                             len(n) for n in row_names if n is not None)) + 2
    else:
        row_names = None
        row_name_width = 0

    if kwargs.get('box_width', None) is not None:
        box_width = kwargs['box_width']
    else:
        box_width = 0
        if kwargs.get('color', False) is False:
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
        box_width += 1      # make sure there is SOME space between!

    if kwargs.get('color', None) is not None:
        format_func = lambda x: "{}{:^{wid}}{}".format(*x, wid=box_width)
    else:
        format_func = lambda x: "{:^{wid}}".format(str(x), wid=box_width)

    if kwargs.get('column_names', None) is not None:
        #  column_names = kwargs['column_names']
        column_names = ' ' * row_name_width
        for nam in kwargs['column_names']:
            column_names += '{:^{wid}}'.format(nam if len(nam) < box_width else
                                               nam[:box_width - 4] + '...',
                                               wid=box_width)
    else:
        column_names = None

    rows = kwargs.get('rows', True)

    # amke the strings!
    res = []
    if rows is False:
        ind = range(len(iterables[0]))
    else:
        ind = range(len(iterables))

    for i in ind:
        if row_names is None:
            r_nam = ''
        else:
            r_nam = "{:>{wid}}: ".format(row_names[i],
                                         wid=row_name_width - 2)
        if rows is False:
            temp = ''.join(list(format_func(it[i]) for it in iterables))
        else:
            temp = ''.join(list(format_func(it) for it in iterables[i]))
        res.append(r_nam + temp)

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
    rw_nams = []
    for i in range(len(test1)):
        rw_nams.append(''.join(random.sample(string.ascii_lowercase,
                                             random.randint(1, 10))))

    frmt_dic = {'column_names': ['a', 'b', 'c', 'd', 'e',
                                 'f', 'g', 'h', 'i', 'h'],
                #  'box_width': 10,
                'row_names': rw_nams}

    res = zygrid(*test1, **frmt_dic)
    print("Testing 10x10 grid...\nresult is {} lines long".format(len(res)))
    for lin in res:
        print(lin)

    # test number two, includes row = False
    print("\nTest 2, 5 columns with 10 rows")
    test2 = []
    for i in range(5):
        test2.append(random.sample(range(1000), 10))

    frmt_dic2 = {'rows':    False
                 }

    res = zygrid(*test2, **frmt_dic2)
    res2 = zygrid(*test2)
    for lin in res:
        print(lin)
    print("Same table, but with 'rows' set to default (True)")
    for lin in res2:
        print(lin)

    # third test... colors!
    print("Testing color formatting & tuple unpacking...")
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

if __name__ == '__main__':
    main()
