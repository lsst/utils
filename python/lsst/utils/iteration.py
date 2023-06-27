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

__all__ = ["chunk_iterable", "ensure_iterable", "isplit"]

import itertools
from collections.abc import Iterable, Iterator, Mapping
from typing import Any, TypeVar


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
