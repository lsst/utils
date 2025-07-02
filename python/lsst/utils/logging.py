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

__all__ = (
    "TRACE",
    "VERBOSE",
    "LsstLogAdapter",
    "LsstLoggers",
    "PeriodicLogger",
    "getLogger",
    "getTraceLogger",
    "trace_set_at",
)

import logging
import sys
import time
from collections.abc import Generator
from contextlib import contextmanager
from logging import LoggerAdapter
from typing import Any, TypeAlias

try:
    import lsst.log.utils as logUtils
except ImportError:
    logUtils = None


# log level for trace (verbose debug).
TRACE = 5
logging.addLevelName(TRACE, "TRACE")

# Verbose logging is midway between INFO and DEBUG.
VERBOSE = (logging.INFO + logging.DEBUG) // 2
logging.addLevelName(VERBOSE, "VERBOSE")


def _calculate_base_stacklevel(default: int, offset: int) -> int:
    """Calculate the default logging stacklevel to use.

    Parameters
    ----------
    default : `int`
        The stacklevel to use in Python 3.11 and newer where the only
        thing to take into account is the number of levels above the core
        Python logging infrastructure.
    offset : `int`
        The offset to apply for older Python implementations that need to
        take into account internal call stacks.

    Returns
    -------
    stacklevel : `int`
        The stack level to pass to internal logging APIs that should result
        in the log messages being reported in caller lines.

    Notes
    -----
    In Python 3.11 the logging infrastructure was fixed such that we no
    longer need to understand that a LoggerAdapter log messages need to
    have a stack level one higher than a Logger would need. ``stacklevel=1``
    now always means "log from the caller's line" without the caller having
    to understand internal implementation details.
    """
    stacklevel = default
    if sys.version_info < (3, 11, 0):
        stacklevel += offset
    return stacklevel


def trace_set_at(name: str, number: int) -> None:
    """Adjust logging level to display messages with the trace number being
    less than or equal to the provided value.

    Parameters
    ----------
    name : `str`
        Name of the logger.
    number : `int`
        The trace number threshold for display.

    Examples
    --------
    .. code-block:: python

       lsst.utils.logging.trace_set_at("lsst.afw", 3)

    This will set loggers ``TRACE0.lsst.afw`` to ``TRACE3.lsst.afw`` to
    ``DEBUG`` and ``TRACE4.lsst.afw`` and ``TRACE5.lsst.afw`` to ``INFO``.

    Notes
    -----
    Loggers ``TRACE0.`` to ``TRACE5.`` are set. All loggers above
    the specified threshold are set to ``INFO`` and those below the threshold
    are set to ``DEBUG``.  The expectation is that ``TRACE`` loggers only
    issue ``DEBUG`` log messages.

    If ``lsst.log`` is installed, this function will also call
    `lsst.log.utils.traceSetAt` to ensure that non-Python loggers are
    also configured correctly.
    """
    for i in range(6):
        level = logging.INFO if i > number else logging.DEBUG
        getTraceLogger(name, i).setLevel(level)

    # if lsst log is available also set the trace loggers there.
    if logUtils is not None:
        logUtils.traceSetAt(name, number)


class _F:
    """Format, supporting `str.format()` syntax.

    Notes
    -----
    This follows the recommendation from
    https://docs.python.org/3/howto/logging-cookbook.html#using-custom-message-objects
    """

    def __init__(self, fmt: str, /, *args: Any, **kwargs: Any):
        self.fmt = fmt
        self.args = args
        self.kwargs = kwargs

    def __str__(self) -> str:
        return self.fmt.format(*self.args, **self.kwargs)


class LsstLogAdapter(LoggerAdapter):
    """A special logging adapter to provide log features for LSST code.

    Expected to be instantiated initially by a call to `getLogger()`.

    This class provides enhancements over `logging.Logger` that include:

    * Methods for issuing trace and verbose level log messages.
    * Provision of a context manager to temporarily change the log level.
    * Attachment of logging level constants to the class to make it easier
      for a Task writer to access a specific log level without having to
      know the underlying logger class.
    """

    # Store logging constants in the class for convenience. This is not
    # something supported by Python loggers but can simplify some
    # logic if the logger is available.
    CRITICAL = logging.CRITICAL
    ERROR = logging.ERROR
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING

    # Python supports these but prefers they are not used.
    FATAL = logging.FATAL
    WARN = logging.WARN

    # These are specific to Tasks
    TRACE = TRACE
    VERBOSE = VERBOSE

    # The stack level to use when issuing log messages. For Python 3.11
    # this is generally 2 (this method and the internal infrastructure).
    # For older python we need one higher because of the extra indirection
    # via LoggingAdapter internals.
    _stacklevel = _calculate_base_stacklevel(2, 1)

    @contextmanager
    def temporary_log_level(self, level: int | str) -> Generator:
        """Temporarily set the level of this logger.

        Parameters
        ----------
        level : `int`
            The new temporary log level.
        """
        old = self.level
        self.setLevel(level)
        try:
            yield
        finally:
            self.setLevel(old)

    @property
    def level(self) -> int:
        """Return current level of this logger (``int``)."""
        return self.logger.level

    def getChild(self, name: str) -> LsstLogAdapter:
        """Get the named child logger.

        Parameters
        ----------
        name : `str`
            Name of the child relative to this logger.

        Returns
        -------
        child : `LsstLogAdapter`
            The child logger.
        """
        return getLogger(name=name, logger=self.logger)

    def _process_stacklevel(self, kwargs: dict[str, Any], offset: int = 0) -> int:
        # Return default stacklevel, taking into account kwargs[stacklevel].
        stacklevel = self._stacklevel
        if "stacklevel" in kwargs:
            # External user expects stacklevel=1 to mean "report from their
            # line" but the code here is already trying to achieve that by
            # default. Therefore if an external stacklevel is specified we
            # adjust their stacklevel request by 1.
            stacklevel = stacklevel + kwargs.pop("stacklevel") - 1

        # The offset can be used to indicate that we have to take into account
        # additional internal layers before calling python logging.
        return _calculate_base_stacklevel(stacklevel, offset)

    def fatal(self, msg: str, *args: Any, **kwargs: Any) -> None:
        # Python does not provide this method in LoggerAdapter but does
        # not formally deprecate it in favor of critical() either.
        # Provide it without deprecation message for consistency with Python.
        # Have to adjust stacklevel on Python 3.10 and older to account
        # for call through self.critical.
        stacklevel = self._process_stacklevel(kwargs, offset=1)
        self.critical(msg, *args, **kwargs, stacklevel=stacklevel)

    def verbose(self, fmt: str, *args: Any, **kwargs: Any) -> None:
        """Issue a VERBOSE level log message.

        Arguments are as for `logging.info`.
        ``VERBOSE`` is between ``DEBUG`` and ``INFO``.

        Parameters
        ----------
        fmt : `str`
            Log message.
        *args : `~typing.Any`
            Parameters references by log message.
        **kwargs : `~typing.Any`
            Parameters forwarded to `log`.
        """
        # There is no other way to achieve this other than a special logger
        # method.
        # Stacklevel is passed in so that the correct line is reported
        stacklevel = self._process_stacklevel(kwargs)
        self.log(VERBOSE, fmt, *args, **kwargs, stacklevel=stacklevel)

    def trace(self, fmt: str, *args: Any, **kwargs: Any) -> None:
        """Issue a TRACE level log message.

        Arguments are as for `logging.info`.
        ``TRACE`` is lower than ``DEBUG``.

        Parameters
        ----------
        fmt : `str`
            Log message.
        *args : `~typing.Any`
            Parameters references by log message.
        **kwargs : `~typing.Any`
            Parameters forwarded to `log`.
        """
        # There is no other way to achieve this other than a special logger
        # method.
        stacklevel = self._process_stacklevel(kwargs)
        self.log(TRACE, fmt, *args, **kwargs, stacklevel=stacklevel)

    def setLevel(self, level: int | str) -> None:
        """Set the level for the logger, trapping lsst.log values.

        Parameters
        ----------
        level : `int`
            The level to use. If the level looks too big to be a Python
            logging level it is assumed to be a lsst.log level.
        """
        if isinstance(level, int) and level > logging.CRITICAL:
            self.logger.warning(
                "Attempting to set level to %d -- looks like an lsst.log level so scaling it accordingly.",
                level,
            )
            level //= 1000

        self.logger.setLevel(level)

    @property
    def handlers(self) -> list[logging.Handler]:
        """Log handlers associated with this logger."""
        return self.logger.handlers

    def addHandler(self, handler: logging.Handler) -> None:
        """Add a handler to this logger.

        Parameters
        ----------
        handler : `logging.Handler`
           Handler to add. The handler is forwarded to the underlying logger.
        """
        self.logger.addHandler(handler)

    def removeHandler(self, handler: logging.Handler) -> None:
        """Remove the given handler from the underlying logger.

        Parameters
        ----------
        handler : `logging.Handler`
            Handler to remove.
        """
        self.logger.removeHandler(handler)


def getLogger(name: str | None = None, logger: logging.Logger | None = None) -> LsstLogAdapter:
    """Get a logger compatible with LSST usage.

    Parameters
    ----------
    name : `str`, optional
        Name of the logger. Root logger if `None`.
    logger : `logging.Logger` or `LsstLogAdapter`
        If given the logger is converted to the relevant logger class.
        If ``name`` is given the logger is assumed to be a child of the
        supplied logger.

    Returns
    -------
    logger : `LsstLogAdapter`
        The relevant logger.

    Notes
    -----
    A `logging.LoggerAdapter` is used since it is easier to provide a more
    uniform interface than when using `logging.setLoggerClass`. An adapter
    can be wrapped around the root logger and the `~logging.setLoggerClass`
    will return the logger first given that name even if the name was
    used before the `~lsst.pipe.base.Task` was created.
    """
    if not logger:
        logger = logging.getLogger(name)
    elif name:
        logger = logger.getChild(name)
    return LsstLogAdapter(logger, {})


LsstLoggers: TypeAlias = logging.Logger | LsstLogAdapter


def getTraceLogger(logger: str | LsstLoggers, trace_level: int) -> LsstLogAdapter:
    """Get a logger with the appropriate TRACE name.

    Parameters
    ----------
    logger : `logging.Logger` or `LsstLogAdapter` or `lsst.log.Log` or `str`
        A logger to be used to derive the new trace logger. Can be a logger
        object that supports the ``name`` property or a string.
    trace_level : `int`
        The trace level to use for the logger.

    Returns
    -------
    trace_logger : `LsstLogAdapter`
        A new trace logger. The name will be derived by pre-pending ``TRACEn.``
        to the name of the supplied logger. If the root logger is given
        the returned logger will be named ``TRACEn``.
    """
    name = getattr(logger, "name", str(logger))
    trace_name = f"TRACE{trace_level}.{name}" if name else f"TRACE{trace_level}"
    return getLogger(trace_name)


class PeriodicLogger:
    """Issue log messages if a time threshold has elapsed.

    This class can be used in long-running sections of code where it would
    be useful to issue a log message periodically to show that the
    algorithm is progressing.

    The first time threshold is counted from object construction, so in general
    the first call to `log` does not log.

    Parameters
    ----------
    logger : `logging.Logger` or `LsstLogAdapter`
        Logger to use when issuing a message.
    interval : `float`
        The minimum interval in seconds between log messages. If `None`,
        `LOGGING_INTERVAL` will be used.
    level : `int`, optional
        Log level to use when issuing messages, default is
        `~logging.INFO`.
    """

    LOGGING_INTERVAL = 600.0
    """Default interval between log messages in seconds."""

    def __init__(self, logger: LsstLoggers, interval: float | None = None, level: int = logging.INFO):
        self.logger = logger
        # None -> LOGGING_INTERVAL conversion done so that unit tests (e.g., in
        # pipe_base) can tweak log interval without access to the constructor.
        self.interval = interval if interval is not None else self.LOGGING_INTERVAL
        self.level = level
        self.next_log_time = time.time() + self.interval
        self.num_issued = 0

        # The stacklevel we need to issue logs is determined by the type
        # of logger we have been given. A LoggerAdapter has an extra
        # level of indirection. In Python 3.11 the logging infrastructure
        # takes care to check for internal logging stack frames so there
        # is no need for a difference.
        self._stacklevel = _calculate_base_stacklevel(2, 1 if isinstance(self.logger, LoggerAdapter) else 0)

    def log(self, msg: str, *args: Any) -> bool:
        """Issue a log message if the interval has elapsed.

        The interval is measured from the previous call to ``log``, or from the
        creation of this object.

        Parameters
        ----------
        msg : `str`
            Message to issue if the time has been exceeded.
        *args : Any
            Arguments to be merged into the message string, as described under
            `logging.Logger.debug`.

        Returns
        -------
        issued : `bool`
            Returns `True` if a log message was sent to the logging system.
            Returns `False` if the interval has not yet elapsed. Returning
            `True` does not indicate whether the log message was in fact
            issued by the logging system.
        """
        if (current_time := time.time()) > self.next_log_time:
            self.logger.log(self.level, msg, *args, stacklevel=self._stacklevel)
            self.next_log_time = current_time + self.interval
            self.num_issued += 1
            return True
        return False
