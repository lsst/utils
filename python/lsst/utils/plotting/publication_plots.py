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

import matplotlib.pyplot

import lsst.utils.plotting

__all__ = [
    "get_band_dicts",
    "set_rubin_plotstyle",
]


def set_rubin_plotstyle():
    """
    Set the matplotlib style for Rubin publications
    """
    matplotlib.pyplot.style.use("lsst.utils.plotting.rubin")
    print("Set up Rubin matplotlib plot style.")


def get_band_dicts():
    """
    Define palettes, from RTN-045.
    Module works with LSST Science Pipelines version >= daily 2024_12_02
    """
    colors_white = lsst.utils.plotting.get_multiband_plot_colors()
    colors_black = lsst.utils.plotting.get_multiband_plot_colors(dark_background=True)
    symbols = lsst.utils.plotting.get_multiband_plot_symbols()
    line_styles = lsst.utils.plotting.get_multiband_plot_linestyles()

    print("This includes dicts for colors_white (bandpass colors for white background),")
    print("  colors_black (bandpass colors for black background), symbols, and line_styles,")
    print("  keyed on band (ugrizy).")

    return {
        "colors_white": colors_white,
        "colors_black": colors_black,
        "symbols": symbols,
        "line_styles": line_styles,
    }
