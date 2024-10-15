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

"""Utilities relating to iterators."""

from __future__ import annotations

__all__ = ["chunk_iterable", "ensure_iterable", "isplit", "sequence_to_string"]

import itertools
from collections.abc import Iterable, Iterator, Mapping
from typing import Any, TypeGuard, TypeVar


def chunk_iterable(data: Iterable[Any], chunk_size: int = 1_000) -> Iterator[tuple[Any, ...]]:
    """Return smaller chunks of an iterable.

    Parameters
    ----------
    data : iterable of anything
        The iterable to be chunked. Can be a mapping, in which case
        the keys are returned in chunks.
    chunk_size : int, optional
        The largest chunk to return. Can be smaller and depends on the
        number of elements in the iterator. Defaults to 1_000.

    Yields
    ------
    chunk : `tuple`
        The contents of a chunk of the iterator as a `tuple`. A tuple is
        preferred over an iterator since it is more convenient to tell it is
        empty and the caller knows it can be sized and indexed.
    """
    it = iter(data)
    while chunk := tuple(itertools.islice(it, chunk_size)):
        yield chunk


def ensure_iterable(a: Any) -> Iterable[Any]:
    """Ensure that the input is iterable.

    There are multiple cases, when the input is:

    - iterable, but not a `str`  or Mapping -> iterate over elements
      (e.g. ``[i for i in a]``)
    - a `str` -> return single element iterable (e.g. ``[a]``)
    - a Mapping -> return single element iterable
    - not iterable -> return single element iterable (e.g. ``[a]``).

    Parameters
    ----------
    a : iterable or `str` or not iterable
        Argument to be converted to an iterable.

    Returns
    -------
    i : `~collections.abc.Iterable`
        Iterable version of the input value.
    """
    if isinstance(a, str):
        yield a
        return
    if isinstance(a, Mapping):
        yield a
        return
    try:
        yield from a
    except Exception:
        yield a


T = TypeVar("T", str, bytes)


def isplit(string: T, sep: T) -> Iterator[T]:
    """Split a string or bytes by separator returning a generator.

    Parameters
    ----------
    string : `str` or `bytes`
        The string to split into substrings.
    sep : `str` or `bytes`
        The separator to use to split the string. Must be the same
        type as ``string``. Must always be given.

    Yields
    ------
    subset : `str` or `bytes`
        The next subset extracted from the input until the next separator.
    """
    if type(string) is not type(sep):
        raise TypeError(f"String and separator types must match ({type(string)} != {type(sep)})")
    begin = 0
    while True:
        end = string.find(sep, begin)
        if end == -1:
            yield string[begin:]
            return
        yield string[begin:end]
        begin = end + 1


def _extract_numeric_suffix(s: str) -> tuple[str, int | None]:
    """Extract the numeric suffix from a string.

    Returns the prefix and the numeric suffix as an integer, if present.

    For example:
    'node1' -> ('node', 1)
    'node' -> ('node', None)
    'node123abc' -> ('node123abc', None)

    Parameters
    ----------
    s : str
        The string to extract the numeric suffix from.

    Returns
    -------
    suffix : str
        The numeric suffix of the string, if any.
    """
    index = len(s)
    while index > 0 and s[index - 1].isdigit():
        index -= 1
    prefix = s[:index]
    suffix = s[index:]
    if suffix:
        return prefix, int(suffix)
    else:
        return s, None


def _add_pair_to_name(val_name: list[str], val0: int | str, val1: int | str, stride: int = 1) -> None:
    """Format a pair of values (val0 and val1) and appends the result to
    val_name.

    This helper function takes the starting and ending values of a sequence
    and formats them into a compact string representation, considering the
    stride and whether the values are integers or strings with common
    prefixes.

    Parameters
    ----------
    val_name : List[str]
        The list to append the formatted string to.
    val0 : [int, str]
        The starting value of the sequence.
    val1 : [int, str]
        The ending value of the sequence.
    stride : int, optional
        The stride or difference between consecutive numbers in the
        sequence. Defaults to 1.
    """
    if isinstance(val0, str) and isinstance(val1, str):
        prefix0, num_suffix0 = _extract_numeric_suffix(val0)
        prefix1, num_suffix1 = _extract_numeric_suffix(val1)
        if prefix0 == prefix1 and num_suffix0 is not None and num_suffix1 is not None:
            if num_suffix0 == num_suffix1:
                dvn = val0
            else:
                dvn = f"{val0}..{val1}"
                if stride > 1:
                    dvn += f":{stride}"
        else:
            dvn = val0 if val0 == val1 else f"{val0}^{val1}"
    else:
        sval0 = str(val0)
        sval1 = str(val1)
        if val0 == val1:
            dvn = sval0
        elif isinstance(val0, int) and isinstance(val1, int):
            if val1 == val0 + stride:
                dvn = f"{sval0}^{sval1}"
            else:
                dvn = f"{sval0}..{sval1}"
                if stride > 1:
                    dvn += f":{stride}"
        else:
            dvn = f"{sval0}^{sval1}"
    val_name.append(dvn)


def _is_list_of_ints(values: list[int | str]) -> TypeGuard[list[int]]:
    """Check if a list is composed entirely of integers.

    Parameters
    ----------
    values : List[int, str]:
        The list of values to check.

    Returns
    -------
    is_ints : bool
        True if all values are integers, False otherwise.
    """
    return all(isinstance(v, int) for v in values)


def sequence_to_string(values: list[int | str]) -> str:
    """Convert a list of integers or strings into a compact string
    representation by merging consecutive values or sequences.

    This function takes a list of integers or strings, sorts them, identifies
    sequences where consecutive numbers differ by a consistent stride, or
    strings with common prefixes, and returns a string that compactly
    represents these sequences. Consecutive numbers are merged into ranges, and
    strings with common prefixes are handled to produce a concise
    representation.

    >>> getNameOfSet([1, 2, 3, 5, 7, 8, 9])
    '1..3^5^7..9'
    >>> getNameOfSet(['node1', 'node2', 'node3'])
    'node1..node3'
    >>> getNameOfSet([10, 20, 30, 40])
    '10..40:10'

    Parameters
    ----------
    values : list[int, str]:
        A list of items to be compacted. Must all be of the same type.

    Returns
    -------
    sequence_as_string : str
        A compact string representation of the input list.

    Notes
    -----
        - The function handles both integers and strings.
        - For strings with common prefixes, only the differing suffixes are
            considered.
        - The stride is determined as the minimum difference between
            consecutive numbers.
        - Strings without common prefixes are listed individually.
    """
    if not values:
        return ""

    values = sorted(set(values))

    pure_ints_or_pure_strings = all(isinstance(item, int) for item in values) or all(
        isinstance(item, str) for item in values
    )
    if not pure_ints_or_pure_strings:
        types = set(type(item) for item in values)
        raise TypeError(f"All items in the input list must be either integers or strings, got {types}")

    # Determine the stride for integers
    stride = 1
    if len(values) > 1 and _is_list_of_ints(values):
        differences = [values[i + 1] - values[i] for i in range(len(values) - 1)]
        stride = min(differences) if differences else 1
        stride = max(stride, 1)

    val_name: list[str] = []
    val0 = values[0]
    val1 = val0
    for val in values[1:]:
        if isinstance(val, int):
            assert isinstance(val1, int)
            if val == val1 + stride:
                val1 = val
            else:
                _add_pair_to_name(val_name, val0, val1, stride)
                val0 = val
                val1 = val0
        elif isinstance(val, str):
            assert isinstance(val1, str)
            prefix1, num_suffix1 = _extract_numeric_suffix(val1)
            prefix, num_suffix = _extract_numeric_suffix(val)
            if prefix1 == prefix and num_suffix1 is not None and num_suffix is not None:
                if num_suffix == num_suffix1 + stride:
                    val1 = val
                else:
                    _add_pair_to_name(val_name, val0, val1)
                    val0 = val
                    val1 = val0
            else:
                _add_pair_to_name(val_name, val0, val1)
                val0 = val
                val1 = val0

    _add_pair_to_name(val_name, val0, val1, stride)

    return "^".join(val_name)
