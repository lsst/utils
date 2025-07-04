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

__all__ = [
    "get_multiband_plot_colors",
    "get_multiband_plot_linestyles",
    "get_multiband_plot_symbols",
    "make_figure",
]

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


def get_multiband_plot_colors(dark_background: bool = False) -> dict:
    """Get color mappings for multiband plots using SDSS filter names.

    Notes
    -----
    From https://rtn-045.lsst.io/#colorblind-friendly-plots

    Parameters
    ----------
    dark_background : `bool`, optional
        Use colors intended for a dark background.
        Default colors are intended for a light background.

    Returns
    -------
    plot_colors : `dict` of `str`
        Mapping of the LSST bands to colors.
    """
    plot_filter_colors_white_background = {
        "u": "#1600EA",
        "g": "#31DE1F",
        "r": "#B52626",
        "i": "#370201",
        "z": "#BA52FF",
        "y": "#61A2B3",
    }
    plot_filter_colors_black_background = {
        "u": "#3eb7ff",
        "g": "#30c39f",
        "r": "#ff7e00",
        "i": "#2af5ff",
        "z": "#a7f9c1",
        "y": "#fdc900",
    }
    if dark_background:
        return plot_filter_colors_black_background
    else:
        return plot_filter_colors_white_background


def get_multiband_plot_symbols() -> dict:
    """Get symbol mappings for multiband plots using SDSS filter names.

    Notes
    -----
    From https://rtn-045.lsst.io/#colorblind-friendly-plots

    Returns
    -------
    plot_symbols : `dict` of `str`
        Mapping of the LSST bands to symbols.
    """
    plot_symbols = {
        "u": "o",
        "g": "^",
        "r": "v",
        "i": "s",
        "z": "*",
        "y": "p",
    }
    return plot_symbols


def get_multiband_plot_linestyles() -> dict:
    """Get line style mappings for multiband plots using SDSS filter names.

    Notes
    -----
    From https://rtn-045.lsst.io/#colorblind-friendly-plots

    Returns
    -------
    plot_linestyles : `dict` of `str`
        Mapping of the LSST bands to line styles.
    """
    plot_line_styles = {
        "u": "--",
        "g": (0, (3, 1, 1, 1)),
        "r": "-.",
        "i": "-",
        "z": (0, (3, 1, 1, 1, 1, 1)),
        "y": ":",
    }

    # [SP-2200]: Restored to using parametric values.
    # To avoid matplotlib v3.10 bug (see DM-49724),
    # manually iterate over `patches` object returned
    # by `plt.hist` when using histtype='step':
    #     _, _, patches = plt.hist()
    #     linestyle = plot_line_styles[band]
    #     for patch in patches:
    #         patch.set_linestyle(linestyle)
    # It seems the bug will be fixed in matplotlib v.3.10.2,
    # see DM-49724[TODO]
    return plot_line_styles
