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

import deprecated.sphinx
import functools


def deprecate_pybind11(obj, reason, category=FutureWarning):
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
    category : `Warning`
        Warning category, passed to `~deprecated.sphinx.deprecated`

    Returns
    -------
    obj : function, method, or class
        Wrapped function, method, or class

    Examples
    -------
    .. code-block:: python

    ExposureF.getCalib = deprecate_pybind11(ExposureF.getCalib,
            reason="Replaced by getPhotoCalib. (Will be removed in 18.0)",
            category=FutureWarning))
    """

    @functools.wraps(obj)
    def internal(*args, **kwargs):
        return obj(*args, **kwargs)

    return deprecated.sphinx.deprecated(reason=reason, category=category)(internal)
