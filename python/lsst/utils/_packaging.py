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

"""Functions to help find packages."""

__all__ = ("getPackageDir",)

import os


def getPackageDir(package_name: str) -> str:
    """Find the file system location of the EUPS package.

    Parameters
    ----------
    package_name : `str`
        The name of the EUPS package.

    Returns
    -------
    path : `str`
        The path to the root of the EUPS package.

    Raises
    ------
    LookupError
        Raised if no product of that name could be found.
    ValueError
        The supplied package name was either not a string or was
        a string of zero-length.

    Notes
    -----
    Does not use EUPS directly. Uses the environment.
    """
    if not package_name or not isinstance(package_name, str):
        raise ValueError(f"EUPS package name '{package_name}' is not of a suitable form.")

    envvar = f"{package_name.upper()}_DIR"

    path = os.environ.get(envvar)
    if path is None:
        raise LookupError(f"Package {package_name} not found")
    return path
