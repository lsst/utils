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

__all__ = ("demangleType",)

"""Functions that have been moved to the cpputils package and should no
longer be used from this package."""

from deprecated.sphinx import deprecated

_REASON = "This function has been moved to the cpputils package. Will be removed after v25."
_VERSION_REMOVED = "v23"


@deprecated(reason=_REASON, version=_VERSION_REMOVED, category=FutureWarning)
def demangleType(type_name: str) -> str:
    """Demangle a C++ type string."""
    import lsst.cpputils

    return lsst.cpputils.demangleType(type_name)
