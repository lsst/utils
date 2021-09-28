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

"""Utilities for measuring execution time.
"""
__all__ = ["logInfo", "timeMethod"]

import functools
import logging
import resource
import time
import datetime

from typing import (
    Any,
    MutableMapping,
)


def _add_to_metadata(metadata: MutableMapping, name: str, value: Any) -> None:
    """Add a value to dict-like object, creating list as needed.

    The list grows as more values are added for that key.

    Parameters
    ----------
    metadata : `dict`-like, optional
        `dict`-like object that can store keys. Uses `add()` method if
        one is available, else creates list and appends value if needed.
    name : `str`
        The key to use in the metadata dictionary.
    value : Any
        Value to store in the list.
    """
    try:
        try:
            # PropertySet should always prefer LongLong for integers
            metadata.addLongLong(name, value)
        except TypeError:
            metadata.add(name, value)
    except AttributeError:
        pass
    else:
        return

    # Fallback code where `add` is not implemented.
    if name not in metadata:
        metadata[name] = []
    metadata[name].append(value)


def logPairs(obj, pairs, logLevel=logging.DEBUG, metadata=None, logger=None):
    """Log ``(name, value)`` pairs to ``obj.metadata`` and ``obj.log``

    Parameters
    ----------
    obj : `object`
        An object with one or both of these two attributes:

        - ``metadata`` a `dict`-like container for storing metadata.
          Can use the ``add(name, value)`` method if found, else will append
          entries to a list.
        - ``log`` an instance of `logging.Logger` or subclass.

        If `None`, at least one of ``metadata`` or ``logger`` should be passed
        or this function will do nothing.
    pairs : sequence
        A sequence of ``(name, value)`` pairs, with value typically numeric.
    logLevel : `int, optional
        Log level (an `logging` level constant, such as `logging.DEBUG`).
    metadata : `collections.abc.MutableMapping`, optional
        Metadata object to write entries to.  Ignored if `None`.
    logger : `logging.Logger`
        Log object to write entries to.  Ignored if `None`.
    """
    if obj is not None:
        if metadata is None:
            try:
                metadata = obj.metadata
            except AttributeError:
                pass
        if logger is None:
            try:
                logger = obj.log
            except AttributeError:
                pass
    strList = []
    for name, value in pairs:
        if metadata is not None:
            _add_to_metadata(metadata, name, value)
        strList.append(f"{name}={value}")
    if logger is not None:
        logging.getLogger("timer." + logger.name).log(logLevel, "; ".join(strList))


def logInfo(obj, prefix, logLevel=logging.DEBUG, metadata=None, logger=None):
    """Log timer information to ``obj.metadata`` and ``obj.log``.

    Parameters
    ----------
    obj : `object`
        An object with both or one these two attributes:

        - ``metadata`` a `dict`-like container for storing metadata.
          Can use the ``add(name, value)`` method if found, else will append
          entries to a list.
        - ``log`` an instance of `logging.Logger` or subclass.

        If `None`, at least one of ``metadata`` or ``logger`` should be passed
        or this function will do nothing.
    prefix
        Name prefix, the resulting entries are ``CpuTime``, etc.. For example
        `timeMethod` uses ``prefix = Start`` when the method begins and
        ``prefix = End`` when the method ends.
    logLevel : optional
        Log level (a `logging` level constant, such as `logging.DEBUG`).
    metadata : `collections.abc.MutableMapping`, optional
        Metadata object to write entries to, overriding ``obj.metadata``.
    logger : `logging.Logger`
        Log object to write entries to, overriding ``obj.log``.

    Notes
    -----
    Logged items include:

    - ``Utc``: UTC date in ISO format (only in metadata since log entries have
      timestamps).
    - ``CpuTime``: System + User CPU time (seconds). This should only be used
        in differential measurements; the time reference point is undefined.
    - ``MaxRss``: maximum resident set size.

    All logged resource information is only for the current process; child
    processes are excluded.
    """
    cpuTime = time.process_time()
    res = resource.getrusage(resource.RUSAGE_SELF)
    if metadata is None and obj is not None:
        try:
            metadata = obj.metadata
        except AttributeError:
            pass
    if metadata is not None:
        # Log messages already have timestamps.
        utcStr = datetime.datetime.utcnow().isoformat()
        _add_to_metadata(metadata, name=prefix + "Utc", value=utcStr)
    logPairs(obj=obj,
             pairs=[
                 (prefix + "CpuTime", cpuTime),
                 (prefix + "UserTime", res.ru_utime),
                 (prefix + "SystemTime", res.ru_stime),
                 (prefix + "MaxResidentSetSize", int(res.ru_maxrss)),
                 (prefix + "MinorPageFaults", int(res.ru_minflt)),
                 (prefix + "MajorPageFaults", int(res.ru_majflt)),
                 (prefix + "BlockInputs", int(res.ru_inblock)),
                 (prefix + "BlockOutputs", int(res.ru_oublock)),
                 (prefix + "VoluntaryContextSwitches", int(res.ru_nvcsw)),
                 (prefix + "InvoluntaryContextSwitches", int(res.ru_nivcsw)),
             ],
             logLevel=logLevel,
             metadata=metadata,
             logger=logger)


def timeMethod(_func=None, *, metadata=None, logger=None,
               logLevel=logging.DEBUG):
    """Decorator to measure duration of a method.

    Parameters
    ----------
    func
        The method to wrap.
    metadata : `collections.abc.MutableMapping`, optional
        Metadata to use as override if the instance object attached
        to this timer does not support a ``metadata`` property.
    logger : `logging.Logger`, optional
        Logger to use when the class containing the decorated method does not
        have a ``log`` property.
    logLevel : `int`, optional
        Log level to use when logging messages. Default is `~logging.DEBUG`.

    Notes
    -----
    Writes various measures of time and possibly memory usage to the
    metadata; all items are prefixed with the function name.

    .. warning::

       This decorator only works with instance methods of any class
       with these attributes:

       - ``metadata``: an instance of `collections.abc.Mapping`. The ``add``
         method will be used if available, else entries will be added to a
         list.
       - ``log``: an instance of `logging.Logger` or subclass.

    Examples
    --------
    To use:

    .. code-block:: python

        import lsst.utils as utils
        import lsst.pipe.base as pipeBase
        class FooTask(pipeBase.Task):
            pass

            @utils.timeMethod
            def run(self, ...): # or any other instance method you want to time
                pass
    """

    def decorator_timer(func):
        @functools.wraps(func)
        def wrapper(self, *args, **keyArgs):
            logInfo(obj=self, prefix=func.__name__ + "Start", metadata=metadata, logger=logger,
                    logLevel=logLevel)
            try:
                res = func(self, *args, **keyArgs)
            finally:
                logInfo(obj=self, prefix=func.__name__ + "End", metadata=metadata, logger=logger,
                        logLevel=logLevel)
            return res
        return wrapper

    if _func is None:
        return decorator_timer
    else:
        return decorator_timer(_func)
