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
        if frmt == 'bars':
            import zybar
            res = zybar.zybar(xvals, yvals)
        elif frmt == 'grid':
            import zygrid
            res = zygrid.zygrid(xvals, yvals)
        elif frmt == 'scatter':
            import zyscatter
            res = zyscatter.zyscatter(xvals, yvals)
        else:
            raise ValueError("Wrong format specified: {}".format(frmt))
    except Exception as e:
        raise e
    return res
