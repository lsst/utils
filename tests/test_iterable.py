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
#

import unittest
import lsst.utils.tests
from lsst.utils import flatten


class IterableTestSuite(lsst.utils.tests.TestCase):

    def testSingleNesting(self):
        initial = ([0, 1], [2, 3])
        final = range(4)
        self.assertSequenceEqual(flatten(initial), final)

    def testMultipleNesting(self):
        initial = [0, [1, (2, 3)], 4, [5, 6], (7), 8]
        final = range(9)
        self.assertSequenceEqual(flatten(initial), final)

    def testPartialOrderingInner(self):
        initial = {0, (1, 2), 3}
        flat = flatten(initial)

        # Sets have undefined order, so any permutation of `initial`
        # that has [1, 2] as a subsequence is valid
        subsequenceFound = False
        for i in range(3):
            if list(flat[i:i+2]) == [1, 2]:
                subsequenceFound = True
                break
        self.assertTrue(subsequenceFound)

    def testPartialOrderingOuter(self):
        initial = [0, {1, 2}, 3]
        flat = flatten(initial)

        # Sets have undefined order, so both
        # [0, 1, 2, 3] and [0, 2, 1, 3] are valid outputs
        self.assertEqual(set(flat), set(range(4)))
        self.assertEqual(flat[0], 0)
        self.assertEqual(flat[3], 3)

    def testString(self):
        initial = ["spherical", [3, 4], ["foo", "bar"]]
        final = ["spherical", 3, 4, "foo", "bar"]
        self.assertSequenceEqual(flatten(initial), final)

    def testDict(self):
        initial = {0: "foo", 1.5: {1: "bar", 2: "baz"}, 3: "bak"}
        with self.assertRaises(ValueError):
            flatten(initial)

    def testMixedDict(self):
        initial = ["string", {1: "bar", 2: "baz"}, 3]
        with self.assertRaises(ValueError):
            flatten(initial)


if __name__ == "__main__":
    unittest.main()
