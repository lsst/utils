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
"""Temporary forwarding of backtrace to cpputils package."""

__all__ = ["isEnabled"]

from deprecated.sphinx import deprecated

try:
    # For now, ensure that backtrace has been imported if somebody
    # is relying on it from a lsst.utils import. Treat it as an optional
    # import.
    import lsst.cpputils.backtrace
except ImportError:
    pass

from .._forwarded import _REASON, _VERSION_REMOVED


@deprecated(reason=_REASON, version=_VERSION_REMOVED, category=FutureWarning)
def isEnabled() -> bool:
    """Check that backtrace is enabled."""
    from lsst.cpputils import backtrace

    return backtrace.isEnabled()
