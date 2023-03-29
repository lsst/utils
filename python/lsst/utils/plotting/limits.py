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

from collections.abc import Sequence
from typing import Optional

import numpy as np


def calculate_safe_plotting_limits(
    data_series: Sequence,  # a sequence of sequences is still a sequence
    percentile: float = 99.9,
    constant_extra: Optional[float] = None,
    symmetric_around_zero: bool = False,
) -> tuple[float, float]:
    """Calculate the right limits for plotting for one or more data series.

    Given one or more data series with potential outliers, calculated the
    values to pass for ymin, ymax so that extreme outliers don't ruin the plot.
    If you are plotting several series on a single axis, pass them all in and
    the overall plotting range will be given.

    Parameters
    ----------
    data_series : `iterable` or `iterable` or `iterable`
        One or more data series which will be going on the same axis, and
        therefore want to have their common plotting limits calculated.
    percentile : `float`, optional
        The percentile used to clip the outliers from the data.
    constant_extra : `float`, optional
        The amount that's added on each side of the range so that data does not
        quite touch the axes. If the default ``None`` is left then 5% of the
        data range is added for cosmetics, but if zero is set this will
        overrides this behaviour and zero you will get.
    symmetric_around_zero : `bool`, optional
        Make the limits symmetric around zero?
    Returns
    -------
    ymin : `float`
        The value to set the ylim minimum to.
    ymax : `float`
        The value to set the ylim maximum to.
    """
    if not isinstance(data_series, Sequence):
        raise ValueError("data_series must be either an iterable, or an iterable of iterables")

    # now we're sure we have an iterable, if it's just one make it a list of it
    # lsst.utils.ensure_iterable is not suitable here as we already have one,
    # we would need ensure_iterable_of_iterables here
    if not isinstance(data_series[0], Sequence):  # we have a single data series, not multiple
        data_series = [data_series]  # now we can iterate like we had more than one

    mins = []
    maxs = []

    for data in data_series:
        max_val = np.nanpercentile(data, percentile)
        min_val = np.nanpercentile(data, 100 - percentile)

        if constant_extra is None:
            data_range = max_val - min_val
            constant_extra = 0.05 * data_range

        max_val += constant_extra
        min_val -= constant_extra

        maxs.append(max_val)
        mins.append(min_val)

    max_val = max(maxs)
    min_val = min(mins)

    if symmetric_around_zero:
        biggest_abs = max(abs(min_val), abs(max_val))
        return -biggest_abs, biggest_abs

    return min_val, max_val
