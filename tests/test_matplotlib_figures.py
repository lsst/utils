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
from lsst.utils.plotting import make_figure

try:
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

            ax = fig.add_subplot(111)
            ax.plot([0, 1], [0, 1], "r-")

            fig.savefig(tmpFile)
