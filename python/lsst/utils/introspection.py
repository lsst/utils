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
    "find_outside_stacklevel",
    "get_caller_name",
    "get_class_of",
    "get_full_type_name",
    "get_instance_of",
    "take_object_census",
    "trace_object_references",
]

import builtins
import collections
import gc
import inspect
import itertools
import sys
import types
import warnings
from collections.abc import Set
from typing import Any

from .doImport import doImport, doImportType


def get_full_type_name(cls_: Any) -> str:
    """Return full type name of the supplied entity.

    Parameters
    ----------
    cls_ : `type` or `object`
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
    if isinstance(cls_, types.ModuleType):
        return cls_.__name__
    # If we have an instance we need to convert to a type
    if not hasattr(cls_, "__qualname__"):
        cls_ = type(cls_)
    if hasattr(builtins, cls_.__qualname__):
        # Special case builtins such as str and dict
        return cls_.__qualname__

    real_name = cls_.__module__ + "." + cls_.__qualname__

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
        if test is not cls_:
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
    *args : `tuple`
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


def find_outside_stacklevel(
    *module_names: str,
    allow_modules: Set[str] = frozenset(),
    allow_methods: Set[str] = frozenset(),
    stack_info: dict[str, Any] | None = None,
) -> int:
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
    allow_methods : `set` [`str`]
        Method names that are allowed to be treated as "outside". Fully
        qualified method names must match exactly. Method names without
        path components will match solely the method name itself. On Python
        3.10 fully qualified names are not supported.
    stack_info : `dict` or `None`, optional
        If given, the dictionary is filled with information from
        the relevant stack frame. This can be used to form your own warning
        message without having to call :func:`inspect.stack` yourself with
        the stack level.

    Returns
    -------
    stacklevel : `int`
        The stacklevel to use matching the first stack frame outside of the
        given module.

    Examples
    --------
    .. code-block:: python

        warnings.warn(
            "A warning message", stacklevel=find_outside_stacklevel("lsst.daf")
        )
    """
    if sys.version_info < (3, 11, 0):
        short_names = {m for m in allow_methods if "." not in m}
        if len(short_names) != len(allow_methods):
            warnings.warn(
                "Python 3.10 does not support fully qualified names in allow_methods. Dropping them.",
                stacklevel=2,
            )
            allow_methods = short_names

    need_full_names = any("." in m for m in allow_methods)

    if stack_info is not None:
        # Ensure it is empty when we start.
        stack_info.clear()

    stacklevel = -1
    for i, s in enumerate(inspect.stack()):
        # This function is never going to be the right answer.
        if i == 0:
            continue
        module = inspect.getmodule(s.frame)
        if module is None:
            continue

        if stack_info is not None:
            stack_info["filename"] = s.filename
            stack_info["lineno"] = s.lineno
            stack_info["name"] = s.frame.f_code.co_name

        if allow_methods:
            code = s.frame.f_code
            names = {code.co_name}  # The name of the function itself.
            if need_full_names:
                full_name = f"{module.__name__}.{code.co_qualname}"
                names.add(full_name)
            if names & allow_methods:
                # Method name is allowed so we stop here.
                del s
                stacklevel = i
                break

        # Stack frames sometimes hang around so explicitly delete.
        del s

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


def take_object_census() -> collections.Counter[type]:
    """Count the number of existing objects, by type.

    The census is returned as a `~collections.Counter` object. Expected usage
    involves taking the difference with a different `~collections.Counter` and
    examining any changes.

    Returns
    -------
    census : `collections.Counter` [`type`]
        The number of objects found of each type.

    Notes
    -----
    This function counts *all* Python objects in memory. To count only
    reachable objects, run `gc.collect` first.
    """
    counts: collections.Counter[type] = collections.Counter()
    for obj in gc.get_objects():
        counts[type(obj)] += 1
    return counts


def trace_object_references(
    target_class: type,
    count: int = 5,
    max_level: int = 10,
) -> tuple[list[list], bool]:
    """Find the chain(s) of references that make(s) objects of a class
    reachable.

    Parameters
    ----------
    target_class : `type`
        The class whose objects need to be traced. This is typically a class
        that is known to be leaking.
    count : `int`, optional
        The number of example objects to trace, if that many exist.
    max_level : `int`, optional
        The number of levels of references to trace. ``max_level=1`` means
        finding only objects that directly refer to the examples.

    Returns
    -------
    traces : `list` [`list`]
        A sequence whose first element (index 0) is the set of example objects
        of type ``target_class``, whose second element (index 1) is the set of
        objects that refer to the examples, and so on. Contains at most
        ``max_level + 1`` elements.
    trace_complete : `bool`
        `True` if the trace for all objects terminated in at most
        ``max_level`` references, and `False` if more references exist.

    Examples
    --------
    An example with two levels of references:

    >>> from collections import namedtuple
    >>> class Foo:
    ...     pass
    >>> holder = namedtuple("Holder", ["bar", "baz"])
    >>> myholder = holder(bar={"object": Foo()}, baz=42)
    >>> # In doctest, the trace extends up to the whole global dict
    >>> # if you let it.
    >>> trace_object_references(Foo, max_level=2)  # doctest: +ELLIPSIS
    ... # doctest: +NORMALIZE_WHITESPACE
    ([[<lsst.utils.introspection.Foo object at ...>],
      [{'object': <lsst.utils.introspection.Foo object at ...>}],
      [Holder(bar={'object': <lsst.utils.introspection.Foo object at ...>},
              baz=42)]], False)
    """

    def class_filter(o: Any) -> bool:
        return isinstance(o, target_class)

    # set() would be more appropriate, but objects may not be hashable.
    objs = list(itertools.islice(filter(class_filter, gc.get_objects()), count))
    if objs:
        return _recurse_trace(objs, remaining=max_level)
    else:
        return [objs], True


def _recurse_trace(objs: list, remaining: int) -> tuple[list[list], bool]:
    """Recursively find references to a set of objects.

    Parameters
    ----------
    objs : `list`
        The objects to trace.
    remaining : `int`
        The number of levels of references to trace.

    Returns
    -------
    traces : `list` [`list`]
        A sequence whose first element (index 0) is ``objs``, whose second
        element (index 1) is the set of objects that refer to those, and so on.
        Contains at most ``remaining + 1``.
    trace_complete : `bool`
        `True` if the trace for all objects terminated in at most
        ``remaining`` references, and `False` if more references exist.
    """
    # Filter out our own references to the objects. This is needed to avoid
    # circular recursion.
    refs = _get_clean_refs(objs)

    if refs:
        if remaining > 1:
            more_refs, complete = _recurse_trace(refs, remaining=remaining - 1)
            more_refs.insert(0, objs)
            return more_refs, complete
        else:
            more_refs = _get_clean_refs(refs)
            return [objs, refs], (not more_refs)
    else:
        return [objs], True


def _get_clean_refs(objects: list) -> list:
    """Find references to a set of objects, excluding those needed to query
    for references.

    Parameters
    ----------
    objects : `list`
        The objects to find references for.

    Returns
    -------
    refs : `list`
        The objects that refer to the elements of ``objects``, not counting
        ``objects`` itself.
    """
    refs = gc.get_referrers(*objects)
    refs.remove(objects)
    iterators = [x for x in refs if type(x).__name__.endswith("_iterator")]
    for i in iterators:
        refs.remove(i)
    return refs
