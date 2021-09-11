# This file is part of utils.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (http://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__all__ = ("demangleType",)

"""Functions that have been moved to the cpputils package and should no
longer be used from this package."""

from deprecated.sphinx import deprecated

_reason = "This function has been moved to the cpputils package. Will be removed after v25."
_version_removed = "v23"


@deprecated(reason=_reason, version=_version_removed, category=FutureWarning)
def demangleType(type_name: str) -> str:
    import lsst.cpputils
    return lsst.cpputils.demangleType(type_name)


@deprecated(reason=_reason, version=_version_removed, category=FutureWarning)
def isEnabled() -> bool:
    """Check that backtrace is enabled."""
    from lsst.cpputils import backtrace
    return backtrace.isEnabled()
