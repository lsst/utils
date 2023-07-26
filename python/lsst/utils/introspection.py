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
#
"""Utilities relating to introspection in python."""

from __future__ import annotations

__all__ = [
    "get_class_of",
    "get_full_type_name",
    "get_instance_of",
    "get_caller_name",
    "find_outside_stacklevel",
]

import builtins
import inspect
import types
from collections.abc import Set
from typing import Any

from .doImport import doImport, doImportType


def get_full_type_name(cls: Any) -> str:
    """Return full type name of the supplied entity.

    Parameters
    ----------
    cls : `type` or `object`
        Entity from which to obtain the full name. Can be an instance
        or a `type`.

    Returns
    -------
    name : `str`
        Full name of type.

    Notes
    -----
    Builtins are returned without the ``builtins`` specifier included.  This
    allows `str` to be returned as "str" rather than "builtins.str". Any
    parts of the path that start with a leading underscore are removed
    on the assumption that they are an implementation detail and the
    entity will be hoisted into the parent namespace.
    """
    # If we have a module that needs to be converted directly
    # to a name.
    if isinstance(cls, types.ModuleType):
        return cls.__name__
    # If we have an instance we need to convert to a type
    if not hasattr(cls, "__qualname__"):
        cls = type(cls)
    if hasattr(builtins, cls.__qualname__):
        # Special case builtins such as str and dict
        return cls.__qualname__

    real_name = cls.__module__ + "." + cls.__qualname__

    # Remove components with leading underscores
    cleaned_name = ".".join(c for c in real_name.split(".") if not c.startswith("_"))

    # Consistency check
    if real_name != cleaned_name:
        try:
            test = doImport(cleaned_name)
        except Exception:
            # Could not import anything so return the real name
            return real_name

        # The thing we imported should match the class we started with
        # despite the clean up. If it does not we return the real name
        if test is not cls:
            return real_name

    return cleaned_name


def get_class_of(typeOrName: type | str | types.ModuleType) -> type:
    """Given the type name or a type, return the python type.

    If a type name is given, an attempt will be made to import the type.

    Parameters
    ----------
    typeOrName : `str` or Python class
        A string describing the Python class to load or a Python type.

    Returns
    -------
    type_ : `type`
        Directly returns the Python type if a type was provided, else
        tries to import the given string and returns the resulting type.

    Notes
    -----
    This is a thin wrapper around `~lsst.utils.doImport`.

    Raises
    ------
    TypeError
        Raised if a module is imported rather than a type.
    """
    if isinstance(typeOrName, str):
        cls = doImportType(typeOrName)
    else:
        if isinstance(typeOrName, types.ModuleType):
            raise TypeError(f"Can not get class of module {get_full_type_name(typeOrName)}")
        cls = typeOrName
    return cls


def get_instance_of(typeOrName: type | str, *args: Any, **kwargs: Any) -> Any:
    """Given the type name or a type, instantiate an object of that type.

    If a type name is given, an attempt will be made to import the type.

    Parameters
    ----------
    typeOrName : `str` or Python class
        A string describing the Python class to load or a Python type.
    args : `tuple`
        Positional arguments to use pass to the object constructor.
    **kwargs
        Keyword arguments to pass to object constructor.

    Returns
    -------
    instance : `object`
        Instance of the requested type, instantiated with the provided
        parameters.

    Raises
    ------
    TypeError
        Raised if a module is imported rather than a type.
    """
    cls = get_class_of(typeOrName)
    return cls(*args, **kwargs)


def get_caller_name(stacklevel: int = 2) -> str:
    """Get the name of the caller method.

    Any item that cannot be determined (or is not relevant, e.g. a free
    function has no class) is silently omitted, along with an
    associated separator.

    Parameters
    ----------
    stacklevel : `int`
        How many levels of stack to skip while getting caller name;
        1 means "who calls me", 2 means "who calls my caller", etc.

    Returns
    -------
    name : `str`
        Name of the caller as a string in the form ``module.class.method``.
        An empty string is returned if ``stacklevel`` exceeds the stack height.

    Notes
    -----
    Adapted from http://stackoverflow.com/a/9812105
    by adding support to get the class from ``parentframe.f_locals['cls']``
    """
    stack = inspect.stack()
    start = 0 + stacklevel
    if len(stack) < start + 1:
        return ""
    parentframe = stack[start][0]

    name = []
    module = inspect.getmodule(parentframe)
    if module:
        name.append(module.__name__)
    # add class name, if any
    if "self" in parentframe.f_locals:
        name.append(type(parentframe.f_locals["self"]).__name__)
    elif "cls" in parentframe.f_locals:
        name.append(parentframe.f_locals["cls"].__name__)
    codename = parentframe.f_code.co_name
    if codename != "<module>":  # top level usually
        name.append(codename)  # function or a method
    return ".".join(name)


def find_outside_stacklevel(*module_names: str, allow_modules: Set[str] = frozenset()) -> int:
    """Find the stacklevel for outside of the given module.

    This can be used to determine the stacklevel parameter that should be
    passed to log messages or warnings in order to make them appear to
    come from external code and not this package.

    Parameters
    ----------
    *module_names : `str`
        The names of the modules to skip when calculating the relevant stack
        level.
    allow_modules : `set` [`str`]
        Names that should not be skipped when calculating the stacklevel.
        If the module name starts with any of the names in this set the
        corresponding stacklevel is used.

    Returns
    -------
    stacklevel : `int`
        The stacklevel to use matching the first stack frame outside of the
        given module.

    Examples
    --------
    .. code-block :: python

        warnings.warn(
            "A warning message",
            stacklevel=find_outside_stacklevel("lsst.daf")
        )
    """
    stacklevel = -1
    for i, s in enumerate(inspect.stack()):
        # This function is never going to be the right answer.
        if i == 0:
            continue
        module = inspect.getmodule(s.frame)
        # Stack frames sometimes hang around so explicitly delete.
        del s
        if module is None:
            continue
        if (
            # The module does not match any of the skipped names.
            not any(module.__name__.startswith(name) for name in module_names)
            # This match is explicitly allowed to be treated as "outside".
            or any(module.__name__.startswith(name) for name in allow_modules)
        ):
            # 0 will be this function.
            # 1 will be the caller
            # and so does not need adjustment.
            stacklevel = i
            break
    else:
        # The top can't be inside the module.
        stacklevel = i

    return stacklevel
