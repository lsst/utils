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

"""Utilities for measuring resource consumption.
"""

import platform
import resource
from typing import Tuple

import psutil
from astropy import units as u

__all__ = ["get_current_mem_usage", "get_peak_mem_usage"]


def get_current_mem_usage() -> Tuple[u.Quantity, u.Quantity]:
    """Report current memory usage.

    Returns
    -------
    usage_main : `astropy.units.Quantity`
        Current memory usage of the calling process expressed in bytes.
    usage_child : `astropy.units.Quantity`
        Current memory usage of the child processes (zero if there are none)
        expressed in bytes.

    Notes
    -----
    Function reports current memory usage using resident set size as a proxy.
    As such the values it reports are capped at available physical RAM and may
    not reflect the actual memory allocated to the process and its children.
    """
    proc = psutil.Process()
    with proc.oneshot():
        usage_main = proc.memory_info().rss * u.byte
        usage_child = sum([child.memory_info().rss for child in proc.children()]) * u.byte
    return usage_main, usage_child


def get_peak_mem_usage() -> Tuple[u.Quantity, u.Quantity]:
    """Report peak memory usage.

    Returns
    -------
    peak_main: `astropy.units.Quantity`
        Peak memory usage (maximum resident set size) of the calling process.
    peak_child: `astropy.units.Quantity`
        Peak memory usage (resident set size) of the largest child process.

    Notes
    -----
    Function reports peak memory usage using the maximum resident set size as
    a proxy. As such the value it reports is capped at available physical RAM
    and may not reflect the actual maximal value.
    """
    # Units getrusage(2) uses to report the maximum resident set size are
    # platform dependent (kilobytes on Linux, bytes on OSX).
    unit = u.kibibyte if platform.system() == "Linux" else u.byte

    peak_main = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * unit
    peak_child = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * unit
    return peak_main, peak_child
