#
# LSST Data Management System
#
# Copyright 2008-2017  AURA/LSST.
#
# This product includes software developed by the
# LSST Project (http://www.lsst.org/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the LSST License Statement and
# the GNU General Public License along with this program.  If not,
# see <https://www.lsstcorp.org/LegalNotices/>.
#
from __future__ import absolute_import, division, print_function
import inspect

__all__ = ["get_caller_name"]


def get_caller_name(skip=2):
    """Get the name of the caller as a string in the form module.class.method

    Any item that cannot be determined (or is not relevant, e.g. a free function
    function has no class) is silently omitted, along with an associated separator.
    An empty string is returned if `skip` exceeds the stack height.

    Parameters
    ----------
    skip : int
        How many levels of stack to skip while getting caller name;
        1 means "who calls me", 2 means "who calls my caller", etc.

    Adapted from from http://stackoverflow.com/a/9812105
    by adding support to get the class from parentframe.f_locals['cls']
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
