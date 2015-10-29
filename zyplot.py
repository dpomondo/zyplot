#! /usr/local/bin/python3
# coding=utf-8
#
# -----------------------------------------------------------------------------
#   file:       zyplot.py
#   use:
#
#   author:     dpomondo
#   site:       github.com/dpomondo/zyplot
# -----------------------------------------------------------------------------


def zyplot(xvals, yvals, frmt='bars'):
    try:
        #  import sys
        #  import os
        #  #  home_dir = '/usr/self/bin/zyplot'
        #  home_dir = os.path.abspath('.')
        #  if home_dir not in sys.path:
            #  sys.path.append(home_dir)
        if frmt == 'bars':
            #  from zyplot.plotters import zybar
            import plotters.zybar as zybar
            res = zybar.zybar(xvals, yvals)
        elif frmt == 'grid':
            #  from zyplot.plotters import zygrid
            import plotters.zygrid as zygrid
            res = zygrid.zygrid(xvals, yvals)
        elif frmt == 'scatter':
            #  from zyplot.plotters import zyscatter
            import plotters.zyscatter as zyscatter
            res = zyscatter.zyscatter(xvals, yvals)
        else:
            raise ValueError("Wrong format specified: {}".format(frmt))
    except Exception as e:
        raise e
    return res


def main():
    for forms in ['bars', 'grid', 'scatter', None]:
        try:
            res = zyplot([], [], frmt=forms)
            print("call to zyplot  with '{}' returned: {}".format(forms, res))
        except Exception as e:
            print("Caught the following: {}".format(e))

if __name__ == '__main__':
    main()
