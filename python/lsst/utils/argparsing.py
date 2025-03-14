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

"""Utilities to help with argument parsing in command line interfaces."""

from __future__ import annotations

__all__ = ["AppendDict"]

import argparse
import copy
from collections.abc import Mapping
from typing import Any


class AppendDict(argparse.Action):
    """An action analogous to the built-in 'append' that appends to a `dict`
    instead of a `list`.

    Inputs are assumed to be strings in the form "key=value"; any input that
    does not contain exactly one "=" character is invalid. If the default value
    is non-empty, the default key-value pairs may be overwritten by values from
    the command line.
    """

    def __init__(
        self,
        option_strings: str | list[str],
        dest: str,
        nargs: int | str | None = None,
        const: Any | None = None,
        default: Any | None = None,
        type: type | None = None,
        choices: Any | None = None,
        required: bool = False,
        help: str | None = None,
        metavar: str | None = None,
    ):
        if default is None:
            default = {}
        if not isinstance(default, Mapping):
            argname = option_strings if option_strings else metavar if metavar else dest
            raise TypeError(f"Default for {argname} must be a mapping or None, got {default!r}.")
        super().__init__(option_strings, dest, nargs, const, default, type, choices, required, help, metavar)

    def __call__(
        self, parser: argparse.ArgumentParser, namespace: Any, values: Any, option_string: str | None = None
    ) -> None:
        # argparse doesn't make defensive copies, so namespace.dest may be
        # the same object as self.default. Do the copy ourselves and avoid
        # modifying the object previously in namespace.dest.
        mapping = copy.copy(getattr(namespace, self.dest))

        # Sometimes values is a copy of default instead of an input???
        if isinstance(values, Mapping):
            mapping.update(values)
        else:
            # values may be either a string or list of strings, depending on
            # nargs. Unsafe to test for Sequence, because a scalar string
            # passes.
            if not isinstance(values, list):
                values = [values]
            for value in values:
                vars = value.split("=")
                if len(vars) != 2:
                    raise ValueError(f"Argument {value!r} does not match format 'key=value'.")
                mapping[vars[0]] = vars[1]

        # Other half of the defensive copy.
        setattr(namespace, self.dest, mapping)
