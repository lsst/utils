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
from __future__ import annotations

"""Support for threading and multi-processing."""

__all__ = ["set_thread_envvars", "disable_implicit_threading"]

import os

try:
    from threadpoolctl import threadpool_limits
except ImportError:
    threadpool_limits = None


def set_thread_envvars(num_threads: int = 1, override: bool = False) -> None:
    """Set common threading environment variables to the given value.

    Parameters
    ----------
    num_threads : `int`, optional
        Number of threads to use when setting the environment variable values.
        Default to 1 (disable threading).
    override : `bool`, optional
        Controls whether a previously set value should be over-ridden. Defaults
        to `False`.
    """
    envvars = (
        "OPENBLAS_NUM_THREADS",
        "GOTO_NUM_THREADS",
        "OMP_NUM_THREADS",
        "MKL_NUM_THREADS",
        "MKL_DOMAIN_NUM_THREADS",
        "MPI_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
        "NUMEXPR_MAX_THREADS",
    )

    for var in envvars:
        if override or var not in os.environ:
            os.environ[var] = str(num_threads)


def disable_implicit_threading() -> None:
    """Do whatever is necessary to try to prevent implicit threading.

    Notes
    -----
    Explicitly limits the number of threads allowed to be used by ``numexpr``
    and attempts to limit the number of threads in all APIs supported by
    the ``threadpoolctl`` package.
    """
    # Force one thread and force override.
    set_thread_envvars(1, True)

    try:
        # This must be a deferred import since importing it immediately
        # triggers the environment variable examination.
        # Catch this in case numexpr is not installed.
        import numexpr.utils
    except ImportError:
        pass
    else:
        numexpr.utils.set_num_threads(1)

    # Try to set threads for openblas and openmp
    if threadpool_limits is not None:
        threadpool_limits(limits=1)
