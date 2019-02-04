#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

__all__ = ["flatten"]

from collections.abc import Mapping


def flatten(nested):
    """Flatten an iterable of possibly nested iterables.

    Parameters
    ----------
    nested : iterable
        An iterable that may contain a mix of scalars or other iterables.

    Returns
    -------
    flat : sequence
        A sequence where each iterable element of `nested` has been replaced
        with its elements, in order, and so on recursively. The result
        preserves the iteration order of the inputs.

    Raises
    ------
    ValueError
        Raised if `nested` is or contains a mapping type (such as `dict`).
        While they are iterable, mapping types cannot be converted into
        sequences or subsequences in any reasonable way.

    Examples
    --------
    >>> x = [42, [4, 3, 5]]
    >>> flatten(x)
    [42, 4, 3, 5]
    """
    if isinstance(nested, Mapping):
        raise ValueError("Can't flatten mapping: %s" % nested)

    flat = []
    for x in nested:
        if isinstance(x, (str, bytes)):
            flat.append(x)
        else:
            # Best way to test for an iterable
            # see https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable
            try:
                iter(x)
                flat.extend(flatten(x))
            except TypeError:
                flat.append(x)
    return flat
