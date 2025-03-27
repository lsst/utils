# This file is part of utils.
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

import unittest

import lsst.utils.tests
from lsst.utils.plotting import (
    get_band_dicts,
    get_multiband_plot_colors,
    get_multiband_plot_linestyles,
    get_multiband_plot_symbols,
    make_figure,
    set_rubin_plotstyle,
)

try:
    from matplotlib import rcParams
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure
except ImportError:
    Figure = None


@unittest.skipIf(Figure is None, "matplotlib is not available.")
class MakeFigureTestCase(unittest.TestCase):
    """Tests for make_figure."""

    def testMakeFigure(self):
        with lsst.utils.tests.getTempFilePath(".png") as tmpFile:
            fig = make_figure(figsize=(10, 6), dpi=300)

            self.assertIsInstance(fig, Figure)
            self.assertIsInstance(fig.canvas, FigureCanvasAgg)
            self.assertEqual(fig.get_figwidth(), 10)
            self.assertEqual(fig.get_figheight(), 6)
            self.assertEqual(fig.get_dpi(), 300)

            bands = ["u", "g", "r", "i", "z", "y"]

            ax = fig.add_subplot(111)
            for dark_background in True, False:
                colors = get_multiband_plot_colors(dark_background=dark_background)
                symbols = get_multiband_plot_symbols()
                linestyles = get_multiband_plot_linestyles()

                ax = fig.add_subplot(111)
                for band in bands:
                    ax.plot(
                        [0, 1],
                        [0, 1],
                        c=colors[band],
                        marker=symbols[band],
                        linestyle=linestyles[band],
                    )

            fig.savefig(tmpFile)


@unittest.skipIf(Figure is None, "matplotlib is not available.")
class PublicationPlotsTestCase(unittest.TestCase):
    """Tests for publication_plots."""

    def testMplStyle(self):
        # Set the plot style
        set_rubin_plotstyle()
        # Confirm that the settings took effect by checking one of them
        self.assertEqual(rcParams["errorbar.capsize"], 3.0)

    def testMultibandPlotColors(self):
        bands_dict = get_band_dicts()
        self.assertEqual(bands_dict["colors"]["r"], "#c61c00")
        self.assertEqual(bands_dict["colors_black"]["r"], "#ff7e00")
        self.assertEqual(bands_dict["symbols"]["r"], "v")
        self.assertEqual(bands_dict["line_styles"]["r"], "-")
