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
"""Utilities for making publication-quality figures."""

__all__ = [
    "get_band_dicts",
    "set_rubin_plotstyle",
]

from . import (
    get_multiband_plot_colors,
    get_multiband_plot_linestyles,
    get_multiband_plot_symbols,
)


def set_rubin_plotstyle() -> None:
    """
    Set the matplotlib style for Rubin publications
    """
    from matplotlib import style

    style.use("lsst.utils.plotting.rubin")


def get_band_dicts() -> dict:
    """
    Define palettes, from RTN-045. This includes dicts for colors (bandpass
    colors for white background), colors_black (bandpass colors for
    black background), plot symbols, and line_styles, keyed on band (ugrizy).

    Returns
    -------
    band_dict : `dict` of `dict`
        Dicts of colors, colors_black, symbols, and line_styles,
        keyed on bands 'u', 'g', 'r', 'i', 'z', and 'y'.
    """
    colors = get_multiband_plot_colors()
    colors_black = get_multiband_plot_colors(dark_background=True)
    symbols = get_multiband_plot_symbols()
    line_styles = get_multiband_plot_linestyles()

    return {
        "colors": colors,
        "colors_black": colors_black,
        "symbols": symbols,
        "line_styles": line_styles,
    }
