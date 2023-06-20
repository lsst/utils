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

"""
A type-annotation workaround for ``...`` not having an exposed type in Python
prior to version 3.10.

This module provides ``Ellipsis`` and ``EllipsisType`` symbols that are
conditionally defined to point to the built-in "``...``" singleton and its type
(respectively) at runtime, and an enum class and instance if
`typing.TYPE_CHECKING` is `True` (an approach first suggested
`here <https://github.com/python/typing/issues/684#issuecomment-548203158>`_).
Type checkers should recognize enum literals as singletons, making this pair
behave as expected under ``is`` comparisons and type-narrowing expressions,
such as::

    v: EllipsisType | int
    if v is not Ellipsis:
        v += 2  # type checker should now see v as a pure int

This works best when there is a clear boundary between code that needs to be
type-checked and can use  ``Ellipsis`` instead of a literal "``...``", and
calling code that is either not type-checked or uses `typing.Any` to accept
literal "``...``" values.
"""

from __future__ import annotations

__all__ = ("Ellipsis", "EllipsisType")

import warnings
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from enum import Enum

    class EllipsisType(Enum):
        """The type associated with an `...`"""

        Ellipsis = "..."

    Ellipsis = EllipsisType.Ellipsis

else:
    try:
        # Present in Python >= 3.10
        from types import EllipsisType

        # If EllipsisType is defined then produce a deprecation warning.
        warnings.warn(
            f"Module {__name__} is deprecated for Python 3.10 or later, native type `types.EllipsisType` "
            "should be used instead.",
            DeprecationWarning,
            stacklevel=2,
        )
    except ImportError:
        EllipsisType = type(Ellipsis)
    Ellipsis = Ellipsis
