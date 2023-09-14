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

from __future__ import annotations

__all__ = ("inheritDoc",)

import inspect
from collections.abc import Callable


def inheritDoc(klass: type) -> Callable:
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

    Notes
    -----
    This method naively appends the doc string from the decorated method to the
    doc string of the equivalent method from the given class. No attempt
    is made to ensure that duplicated sections are merged together or
    overwritten.

    This decorator is not necessary to ensure that a parent doc string appears
    in a subclass. Tools like ``pydoc`` and Sphinx handle that automatically.
    This can, though, be used to ensure that a specific docstring from a
    parent class appears if there is ambiguity from multiple inheritance.
    """

    def tmpDecorator(method: type) -> Callable:
        """Update the documentation from a class with the same method."""
        methodName = method.__name__
        if not hasattr(klass, methodName):
            raise AttributeError(f"{klass} has no method named {methodName} to inherit from")

        # To append reliably, the doc strings need to be cleaned to
        # remove indents.
        appendText = inspect.cleandoc(method.__doc__ or "")
        parentText = inspect.cleandoc(getattr(klass, methodName).__doc__ or "")

        if parentText:
            if appendText:
                # cleandoc() strips leading and trailing space so it is safe
                # to add new lines.
                parentText += "\n\n" + appendText
            method.__doc__ = parentText
        else:
            # Do not update the doc string if there was no parent doc string.
            pass
        return method

    return tmpDecorator
