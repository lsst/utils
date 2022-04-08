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

__all__ = ("doImport", "doImportType")

import importlib
import types
from typing import List, Optional, Type, Union


def doImport(importable: str) -> Union[types.ModuleType, Type]:
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

    def tryImport(
        module: str, fromlist: List[str], previousError: Optional[str]
    ) -> Union[types.ModuleType, Type]:
        pytype = importlib.import_module(module)
        # Can have functions inside classes inside modules
        for f in fromlist:
            try:
                pytype = getattr(pytype, f)
            except AttributeError:
                extra = f"({previousError})" if previousError is not None else ""
                raise ImportError(
                    f"Could not get attribute '{f}' from '{module}' when importing '{importable}' {extra}"
                )
        return pytype

    # Go through the import path attempting to load the module
    # and retrieve the class or function as an attribute. Shift components
    # from the module list to the attribute list until something works.
    moduleComponents = importable.split(".")
    infileComponents: List[str] = []
    previousError = None

    while moduleComponents:
        try:
            pytype = tryImport(".".join(moduleComponents), infileComponents, previousError)
            if not infileComponents and hasattr(pytype, moduleComponents[-1]):
                # This module has an attribute with the same name as the
                # module itself (like doImport.doImport, actually!).
                # If that attribute was lifted to the package, we should
                # return the attribute, not the module.
                try:
                    return tryImport(".".join(moduleComponents[:-1]), moduleComponents[-1:], previousError)
                except ModuleNotFoundError:
                    pass
            return pytype
        except ModuleNotFoundError as e:
            previousError = str(e)
            # Move element from module to file and try again
            infileComponents.insert(0, moduleComponents.pop())

    # Fell through without success.
    extra = f"({previousError})" if previousError is not None else ""
    raise ModuleNotFoundError(f"Unable to import {importable!r} {extra}")


def doImportType(importable: str) -> Type:
    """Import a python type given an importable string and return it.

    Parameters
    ----------
    importable : `str`
        String containing dot-separated path of a Python class,
        or member function.

    Returns
    -------
    type : `type`
        Type object. Can not return a module.

    Raises
    ------
    TypeError
        ``importable`` is not a `str` or the imported type is a module.
    ModuleNotFoundError
        No module in the supplied import string could be found.
    ImportError
        ``importable`` is found but can not be imported or the requested
        item could not be retrieved from the imported module.
    """
    imported = doImport(importable)
    if isinstance(imported, types.ModuleType):
        raise TypeError(f"Import of {importable} returned a module and not a type.")
    return imported
