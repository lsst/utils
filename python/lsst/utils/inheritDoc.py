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

__all__ = ("inheritDoc",)

from typing import Callable, Type


def inheritDoc(klass: Type) -> Callable:
    """Extend existing documentation for a method that exists in another
    class and extend it with any additional documentation defined.

    This decorator takes a class from which to draw documentation from as an
    argument. This is so that any class may be used as a source of
    documentation and not just the immediate parent of a class. This is useful
    when there may be a long inheritance chain, or in the case of mixins.

    Parameters
    ----------
    klass : object
        The class to inherit documentation from.

    Returns
    -------
    decorator : callable
        Intermediate decorator used in the documentation process.
    """

    def tmpDecorator(method: Type) -> Callable:
        """Update the documentation from a class with the same method."""
        methodName = method.__name__
        if not hasattr(klass, methodName):
            raise AttributeError(f"{klass} has no method named {methodName} to inherit from")
        appendText = method.__doc__ or ""
        method.__doc__ = getattr(klass, methodName).__doc__ + appendText
        return method

    return tmpDecorator
