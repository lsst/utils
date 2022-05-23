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

__all__ = ("Ellipsis", "EllipsisType")

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Workaround for `...` not having an exposed type in Python, borrowed from
    # https://github.com/python/typing/issues/684#issuecomment-548203158
    # Along with that, we need to either use `Ellipsis` instead of `...` for
    # the actual sentinal value internally, and tell MyPy to ignore conversions
    # from `...` to `Ellipsis` at the public-interface boundary.
    #
    # `Ellipsis` and `EllipsisType` should be directly imported from this
    # module by related code that needs them; hopefully that will stay confined
    # to `lsst.daf.butler.registry`.  Putting these in __all__ is bad for
    # Sphinx, and probably more confusing than helpful overall.
    from enum import Enum

    class EllipsisType(Enum):
        Ellipsis = "..."

    Ellipsis = EllipsisType.Ellipsis

else:
    EllipsisType = type(Ellipsis)
    Ellipsis = Ellipsis
