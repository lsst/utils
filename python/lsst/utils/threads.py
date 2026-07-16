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
"""Support for threading and multi-processing."""

from __future__ import annotations

__all__ = ["disable_implicit_threading", "set_thread_envvars"]

import logging
import os
import sys

try:
    from threadpoolctl import threadpool_limits
except ImportError:
    threadpool_limits = None

_LOG = logging.getLogger(__name__)


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
        "NUMBA_NUM_THREADS",
        "ARROW_IO_THREADS",
        "VECLIB_MAXIMUM_THREADS",
        "RAYON_NUM_THREADS",
        "POLARS_MAX_THREADS",
        "BLIS_NUM_THREADS",
    )

    for var in envvars:
        if override or var not in os.environ:
            os.environ[var] = str(num_threads)

    # Also specify an explicit value for OMP_PROC_BIND to tell OpenMP not to
    # set CPU affinity.
    var = "OMP_PROC_BIND"
    if override or var not in os.environ:
        os.environ[var] = "false"


def disable_implicit_threading() -> None:
    """Do whatever is necessary to try to prevent implicit threading.

    Notes
    -----
    Explicitly limits the number of threads allowed to be used by ``numexpr``
    and ``pyarrow`` (if already imported) and attempts to limit the number of
    threads in all APIs supported by the ``threadpoolctl`` package.
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

    # pyarrow sizes its thread pools from the environment only when each pool
    # is first used, so pools that may already exist must be resized
    # explicitly. If pyarrow has not been imported the environment variables
    # set above are sufficient and there is no need to pay for an import here.
    if (pyarrow := sys.modules.get("pyarrow")) is not None:
        pyarrow.set_cpu_count(1)
        pyarrow.set_io_thread_count(1)

    # numba reads its environment variable only at import time so an
    # already-imported numba must be limited at runtime.
    if (numba := sys.modules.get("numba")) is not None:
        numba.set_num_threads(1)

    # Try to set threads for openblas and openmp
    if threadpool_limits is not None:
        threadpool_limits(limits=1)
    else:
        _LOG.warning(
            "threadpoolctl is not installed: thread pools of already-loaded libraries cannot be "
            "limited and implicit threading may remain enabled."
        )
