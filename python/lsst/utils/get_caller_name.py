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

__all__ = ["get_caller_name"]

from deprecated.sphinx import deprecated

from .introspection import get_caller_name as caller_name


@deprecated(
    reason="get_caller_name has moved to `lsst.utils.introspection.get_caller_name`."
    " Will be removed in v26.",
    version="v24",
    category=FutureWarning,
)
def get_caller_name(skip: int = 2) -> str:
    """Get the name of the caller method.

    Any item that cannot be determined (or is not relevant, e.g. a free
    function has no class) is silently omitted, along with an
    associated separator.

    Parameters
    ----------
    skip : `int`
        How many levels of stack to skip while getting caller name;
        1 means "who calls me", 2 means "who calls my caller", etc.

    Returns
    -------
    name : `str`
        Name of the caller as a string in the form ``module.class.method``.
        An empty string is returned if ``skip`` exceeds the stack height.
    """
    # Offset the stack level to account for redirect and deprecated wrapper.
    return caller_name(stacklevel=skip + 2)
