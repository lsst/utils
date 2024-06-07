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
"""Utilities related to making matplotlib figures."""

from __future__ import annotations

__all__ = ["make_figure"]

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.figure import Figure


def make_figure(**kwargs: Any) -> Figure:
    """Make a matplotlib Figure with an Agg-backend canvas.

    This routine creates a matplotlib figure without using
    ``matplotlib.pyplot``, and instead uses a fixed non-interactive
    backend. The advantage is that these figures are not cached and
    therefore do not need to be explicitly closed -- they
    are completely self-contained and ephemeral unlike figures
    created with `matplotlib.pyplot.figure()`.

    Parameters
    ----------
    **kwargs : `dict`
        Keyword arguments to be passed to `matplotlib.figure.Figure()`.

    Returns
    -------
    figure : `matplotlib.figure.Figure`
        Figure with a fixed Agg backend, and no caching.

    Notes
    -----
    The code here is based on
    https://matplotlib.org/stable/gallery/user_interfaces/canvasagg.html
    """
    try:
        from matplotlib.backends.backend_agg import FigureCanvasAgg
        from matplotlib.figure import Figure
    except ImportError as e:
        raise RuntimeError("Cannot use make_figure without matplotlib.") from e

    fig = Figure(**kwargs)
    FigureCanvasAgg(fig)

    return fig
