# This file is part of lsst.utils.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__all__ = ['deprecate_pybind11', 'suppress_deprecations']

import deprecated.sphinx
import functools
import unittest.mock
import warnings

from contextlib import contextmanager


def deprecate_pybind11(obj, reason, version=None, category=FutureWarning):
    """Deprecate a pybind11-wrapped C++ interface function, method or class.

    This needs to use a pass-through Python wrapper so that
    `~deprecated.sphinx.deprecated` can update its docstring; pybind11
    docstrings are native and cannot be modified.

    Note that this is not a decorator; its output must be assigned to
    replace the method being deprecated.

    Parameters
    ----------
    obj : function, method, or class
        The function, method, or class to deprecate.
    reason : `str`
        Reason for deprecation, passed to `~deprecated.sphinx.deprecated`
    version : 'str'
        Next major version in which the interface will be deprecated,
        passed to `~deprecated.sphinx.deprecated`
    category : `Warning`
        Warning category, passed to `~deprecated.sphinx.deprecated`

    Returns
    -------
    obj : function, method, or class
        Wrapped function, method, or class

    Examples
    --------
    .. code-block:: python

       ExposureF.getCalib = deprecate_pybind11(ExposureF.getCalib,
               reason="Replaced by getPhotoCalib. (Will be removed in 18.0)",
               version="17.0", category=FutureWarning))
    """

    @functools.wraps(obj)
    def internal(*args, **kwargs):
        return obj(*args, **kwargs)

    return deprecated.sphinx.deprecated(
        reason=reason,
        version=version,
        category=category)(internal)


@contextmanager
def suppress_deprecations(category=FutureWarning):
    """Suppress warnings generated by `deprecated.sphinx.deprecated`.

    Naively, one might attempt to suppress these warnings by using
    `~warnings.catch_warnings`. However, `~deprecated.sphinx.deprecated`
    attempts to install its own filter, overriding that. This convenience
    method works around this and properly suppresses the warnings by providing
    a mock `~warnings.simplefilter` for `~deprecated.sphinx.deprecated` to
    call.

    Parameters
    ----------
    category : `Warning` or subclass
        The category of warning to suppress.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category)
        with unittest.mock.patch.object(warnings, "simplefilter"):
            yield
