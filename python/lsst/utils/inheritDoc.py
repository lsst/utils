# This file is part of utils.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (http://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
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
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__all__ = ("inheritDoc",)

from typing import Callable, Type


def inheritDoc(klass: Type) -> Callable:
    """Extends existing documentation for a method that exists in another
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
        """Decorator to update the documentation from a class with the same
        method.
        """
        methodName = method.__name__
        if not hasattr(klass, methodName):
            raise AttributeError(f"{klass} has no method named {methodName} to inherit from")
        appendText = method.__doc__ or ""
        method.__doc__ = getattr(klass, methodName).__doc__ + appendText
        return method
    return tmpDecorator
