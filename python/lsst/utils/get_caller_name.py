# This file is part of utils.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# Use of this source code is governed by a 3-clause BSD-style
# license that can be found in the LICENSE file.

__all__ = ["get_caller_name"]

import inspect


def get_caller_name(skip: int = 2) -> str:
    """Get the name of the caller method.

    Any item that cannot be determined (or is not relevant, e.g. a free
    function has no class) is silently omitted, along with an
    associated separator.

    Parameters
    ----------
    skip : `int`
        How many levels of stack to skip while getting caller name;
        1 means "who calls me", 2 means "who calls my caller", etc.

    Returns
    -------
    name : `str`
        Name of the caller as a string in the form ``module.class.method``.
        An empty string is returned if ``skip`` exceeds the stack height.

    Notes
    -----
    Adapted from from http://stackoverflow.com/a/9812105
    by adding support to get the class from ``parentframe.f_locals['cls']``
    """
    stack = inspect.stack()
    start = 0 + skip
    if len(stack) < start + 1:
        return ''
    parentframe = stack[start][0]

    name = []
    module = inspect.getmodule(parentframe)
    if module:
        name.append(module.__name__)
    # add class name, if any
    if 'self' in parentframe.f_locals:
        name.append(type(parentframe.f_locals['self']).__name__)
    elif 'cls' in parentframe.f_locals:
        name.append(parentframe.f_locals['cls'].__name__)
    codename = parentframe.f_code.co_name
    if codename != '<module>':  # top level usually
        name.append(codename)  # function or a method
    return ".".join(name)
