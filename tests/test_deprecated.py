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

import copy
import unittest
import warnings

import lsst.utils
import lsst.utils.tests
from lsst.utils.deprecated import DeprecatedDict


class DeprecatedDictTestCase(lsst.utils.tests.TestCase):
    """Test `~lsst.utils.deprecated.DeprecatedDict`."""

    def makeDict(self, **kwargs):
        # A DeprecatedDict with one deprecated key ("old") and one live key
        # ("new"). Construction with a non-empty `deprecations` never warns.
        return DeprecatedDict(
            {"old": 1, "new": 2},
            deprecations={"old": "Use `.new` instead."},
            version="v30.0",
            **kwargs,
        )

    def testIsADict(self):
        d = self.makeDict()
        self.assertIsInstance(d, dict)
        self.assertEqual(d["new"], 2)  # Live key never warns.

    def testNoDeprecatedKeysWarns(self):
        with self.assertWarns(UserWarning):
            DeprecatedDict({"a": 1}, deprecations={})

    def testGetItemWarnsOnce(self):
        d = self.makeDict()
        with self.assertWarns(FutureWarning) as cm:
            self.assertEqual(d["old"], 1)
        message = str(cm.warning)
        self.assertIn("v30.0", message)
        self.assertIn("Use `.new` instead.", message)
        # A second access of the same key is silent.
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            self.assertEqual(d["old"], 1)

    def testTargetedAccessorsWarn(self):
        cases = {
            "getitem": lambda d: d["old"],
            "get": lambda d: d.get("old"),
            "pop": lambda d: d.pop("old"),
            "setdefault": lambda d: d.setdefault("old", 9),
            "setitem": lambda d: d.__setitem__("old", 9),
            "delitem": lambda d: d.__delitem__("old"),
        }
        for name, op in cases.items():
            with self.subTest(accessor=name):
                d = self.makeDict()
                with self.assertWarns(FutureWarning):
                    op(d)

    def testCustomCategory(self):
        d = self.makeDict(category=DeprecationWarning)
        with self.assertWarns(DeprecationWarning):
            _ = d["old"]

    def testPerKeyReasonAndCategory(self):
        d = DeprecatedDict(
            {"a": 1, "b": 2},
            deprecations={"a": "Use `.a` instead.", "b": "Use `.b` instead."},
            deprecated_categories={"b": DeprecationWarning},
        )
        # "a" uses the default category and its own reason.
        with self.assertWarns(FutureWarning) as cm:
            _ = d["a"]
        self.assertIn("Use `.a` instead.", str(cm.warning))
        # "b" overrides the category and carries its own reason.
        with self.assertWarns(DeprecationWarning) as cm:
            _ = d["b"]
        self.assertIn("Use `.b` instead.", str(cm.warning))

    def testLiveKeyNeverWarns(self):
        d = self.makeDict()
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            _ = d["new"]
            _ = d.get("new")
            d["new"] = 3

    def testBulkOperationsAreSilent(self):
        d = self.makeDict()
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            self.assertEqual(dict(d), {"old": 1, "new": 2})
            self.assertEqual({**d}, {"old": 1, "new": 2})
            self.assertEqual(sorted(d.keys()), ["new", "old"])
            self.assertEqual(sorted(d.items()), [("new", 2), ("old", 1)])
            self.assertIn("old", d)
            other = {}
            other.update(d)
        self.assertEqual(other, {"old": 1, "new": 2})

    def testDeepcopyIsSilentAndIndependent(self):
        d = self.makeDict()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            _ = d["old"]  # Latch the original.
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            clone = copy.deepcopy(d)
            # The clone inherits the "already warned" latch, so it too is
            # silent for the key already warned on the original.
            _ = clone["old"]
        self.assertIsInstance(clone, DeprecatedDict)
        self.assertEqual(dict(clone), {"old": 1, "new": 2})
        self.assertEqual(dict(clone), dict(d))


class DeprecatedTestCase(lsst.utils.tests.TestCase):
    """Test depreaction."""

    def test_deprecate_pybind11(self):
        def old(x):
            """Docstring."""
            return x + 1

        # Use an unusual category
        old = lsst.utils.deprecate_pybind11(
            old, reason="For testing.", version="unknown", category=PendingDeprecationWarning
        )
        with self.assertWarnsRegex(
            PendingDeprecationWarning,
            r"Call to deprecated function \(or staticmethod\) old\. \(For testing\.\) "
            "-- Deprecated since version unknown.$",
        ):
            # Check that the function still works
            self.assertEqual(old(3), 4)
        self.assertIn("Docstring", old.__doc__)
        self.assertIn("For testing.", old.__doc__)


if __name__ == "__main__":
    unittest.main()
