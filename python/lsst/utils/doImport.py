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


import importlib

__all__ = ("doImport",)


def doImport(importable):
    """Import a python object given an importable string and return it.

    Parameters
    ----------
    importable : `str`
        String containing dot-separated path of a Python class, module,
        or member function.

    Returns
    -------
    type : `type`
        Type object. Either a module or class or a function.

    Raises
    ------
    TypeError
        ``importable`` is not a `str`.
    ModuleNotFoundError
        No module in the supplied import string could be found.
    ImportError
        ``importable`` is found but can not be imported or the requested
        item could not be retrieved from the imported module.
    """
    if not isinstance(importable, str):
        raise TypeError(f"Unhandled type of importable, val: {importable}")

    def tryImport(module, fromlist):
        pytype = importlib.import_module(module)
        # Can have functions inside classes inside modules
        for f in fromlist:
            try:
                pytype = getattr(pytype, f)
            except AttributeError as e:
                raise ImportError(f"Could not get attribute '{f}' from '{module}'")
        return pytype

    # Go through the import path attempting to load the module
    # and retrieve the class or function as an attribute. Shift components
    # from the module list to the attribute list until something works.
    moduleComponents = importable.split(".")
    infileComponents = []

    while moduleComponents:
        try:
            pytype = tryImport(".".join(moduleComponents), infileComponents)
            return pytype
        except ModuleNotFoundError:
            # Move element from module to file and try again
            infileComponents.insert(0, moduleComponents.pop())

    raise ModuleNotFoundError(f"Unable to import {importable}")
