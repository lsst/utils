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
    "accent_color",
    "divergent_cmap",
    "galaxies_cmap",
    "galaxies_color",
    "get_band_dicts",
    "mk_colormap",
    "set_rubin_plotstyle",
    "sso_cmap",
    "sso_color",
    "stars_cmap",
    "stars_color",
]

import numpy as np

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


def mk_colormap(colorNames):  # type: ignore
    """Make a colormap from the list of color names.

    Parameters
    ----------
    colorNames : `list`
        A list of strings that correspond to matplotlib named colors.

    Returns
    -------
    cmap : `matplotlib.colors.LinearSegmentedColormap`
        A colormap stepping through the supplied list of names.
    """
    from matplotlib import colors

    blues = []
    greens = []
    reds = []
    alphas = []

    if len(colorNames) == 1:
        # Alpha is between 0 and 1 really but
        # using 1.5 saturates out the top of the
        # colorscale, this looks good for ComCam data
        # but might want to be changed in the future.
        alphaRange = [0.2, 1.0]
        nums = np.linspace(0, 1, len(alphaRange))
        r, g, b = colors.colorConverter.to_rgb(colorNames[0])
        for num, alpha in zip(nums, alphaRange):
            blues.append((num, b, b))
            greens.append((num, g, g))
            reds.append((num, r, r))
            alphas.append((num, alpha, alpha))

    else:
        nums = np.linspace(0, 1, len(colorNames))
        if len(colorNames) == 3:
            alphaRange = [1.0, 1.0, 1.0]
        elif len(colorNames) == 5:
            alphaRange = [1.0, 0.7, 0.3, 0.7, 1.0]
        else:
            alphaRange = np.ones(len(colorNames))

        for num, color, alpha in zip(nums, colorNames, alphaRange):
            r, g, b = colors.colorConverter.to_rgb(color)
            blues.append((num, b, b))
            greens.append((num, g, g))
            reds.append((num, r, r))
            alphas.append((num, alpha, alpha))

    colorDict = {"blue": blues, "red": reds, "green": greens, "alpha": alphas}
    cmap = colors.LinearSegmentedColormap("newCmap", colorDict)
    return cmap


def divergent_cmap():  # type: ignore
    """
    Make a divergent color map.
    """
    cmap = mk_colormap([stars_color(), "#D9DCDE", accent_color()])

    return cmap


def stars_cmap(single_color=False):  # type: ignore
    """Make a color map for stars."""
    import seaborn as sns
    from matplotlib.colors import ListedColormap

    if single_color:
        cmap = mk_colormap([stars_color()])
    else:
        cmap = ListedColormap(sns.color_palette("mako", 256))
    return cmap


def stars_color() -> str:
    """Return the star color string for lines"""
    return "#084d96"


def accent_color() -> str:
    """Return a contrasting color for overplotting,
    black is the best for this but if you need two colors
    this works well on blue.
    """
    return "#DE8F05"


def galaxies_cmap(single_color=False):  # type: ignore
    """Make a color map for galaxies."""
    if single_color:
        cmap = mk_colormap([galaxies_color()])
    else:
        cmap = "inferno"
    return cmap


def galaxies_color() -> str:
    """Return the galaxy color string for lines"""
    return "#961A45"


def sso_color() -> str:
    """Return the SSO color string for lines"""
    return "#01694c"


def sso_cmap(single_color=False):  # type: ignore
    """Make a color map for solar system objects."""
    if single_color:
        cmap = mk_colormap([sso_color()])
    else:
        cmap = "viridis"
    return cmap


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
