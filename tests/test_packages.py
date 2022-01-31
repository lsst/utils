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
#

import os
import unittest
from collections.abc import Mapping

import lsst.utils.packages
import lsst.utils.tests

TESTDIR = os.path.abspath(os.path.dirname(__file__))


class PackagesTestCase(unittest.TestCase):
    """Tests for package version collection

    Unfortunately, we're somewhat limited in what we can test because
    we only get the versions of things being used at runtime, and this
    package sits rather low in the dependency chain so there's not
    usually a lot of other packages available when this test gets run.
    Therefore some of the tests are only checking that things don't
    explode, since they are incapable of testing much more than that.
    """

    def testPython(self):
        """Test that we get the right version for this python package"""
        versions = lsst.utils.packages.getPythonPackages()
        expected = lsst.utils.version.__version__
        self.assertEqual(versions["utils"], expected)

    def testEnvironment(self):
        """Test getting versions from the environment

        Unfortunately, none of the products that need their versions divined
        from the environment are dependencies of this package, and so all we
        can do is test that this doesn't fall over.
        """
        lsst.utils.packages.getEnvironmentPackages()

    def testConda(self):
        """Test getting versions from conda environement

        We do not rely on being run in a conda environment so all we can do is
        test that this doesn't fall over.
        """
        lsst.utils.packages.getCondaPackages()

    def _writeTempFile(self, packages, suffix):
        """Write packages to a temp file using the supplied suffix and read
        back.
        """
        with lsst.utils.tests.getTempFilePath(suffix) as tempName:
            packages.write(tempName)
            new = lsst.utils.packages.Packages.read(tempName)
        return new

    def testPackages(self):
        """Test the Packages class"""
        packages = lsst.utils.packages.Packages.fromSystem()
        self.assertIsInstance(packages, Mapping)

        # Check that stringification is not crashing.
        self.assertTrue(str(packages).startswith("Packages({"))
        self.assertTrue(repr(packages).startswith("Packages({"))

        # Test pickling and YAML
        new = self._writeTempFile(packages, ".pickle")
        new_pkl = self._writeTempFile(packages, ".pkl")
        new_yaml = self._writeTempFile(packages, ".yaml")
        new_json = self._writeTempFile(packages, ".json")

        self.assertIsInstance(new, lsst.utils.packages.Packages, f"Checking type ({type(new)}) from pickle")
        self.assertIsInstance(
            new_yaml, lsst.utils.packages.Packages, f"Checking type ({type(new_yaml)}) from YAML"
        )
        self.assertEqual(new, packages)
        self.assertEqual(new_pkl, new)
        self.assertEqual(new, new_yaml)
        self.assertEqual(new, new_json)

        # Dict compatibility.
        for k, v in new.items():
            self.assertEqual(new[k], v)

        with self.assertRaises(ValueError):
            self._writeTempFile(packages, ".txt")

        with self.assertRaises(ValueError):
            # .txt extension is not recognized
            lsst.utils.packages.Packages.read("something.txt")

        # 'packages' and 'new' should have identical content
        self.assertDictEqual(packages.difference(new), {})
        self.assertDictEqual(packages.missing(new), {})
        self.assertDictEqual(packages.extra(new), {})
        self.assertEqual(len(packages), len(new))

        # Check inverted comparisons
        self.assertDictEqual(new.difference(packages), {})
        self.assertDictEqual(new.missing(packages), {})
        self.assertDictEqual(new.extra(packages), {})

        # Now load an obscure python package and the list of packages should
        # change
        # Shouldn't be used by anything we've previously imported
        import smtpd  # noqa: F401

        new = lsst.utils.packages.Packages.fromSystem()
        self.assertDictEqual(packages.difference(new), {})  # No inconsistencies
        self.assertDictEqual(packages.extra(new), {})  # Nothing in 'packages' that's not in 'new'
        missing = packages.missing(new)
        self.assertGreater(len(missing), 0)  # 'packages' should be missing some stuff in 'new'
        self.assertIn("smtpd", missing)

        # Inverted comparisons
        self.assertDictEqual(new.difference(packages), {})
        self.assertDictEqual(new.missing(packages), {})  # Nothing in 'new' that's not in 'packages'
        extra = new.extra(packages)
        self.assertGreater(len(extra), 0)  # 'new' has extra stuff compared to 'packages'
        self.assertIn("smtpd", extra)
        self.assertIn("smtpd", new)

        # Run with both a Packages and a dict
        for new_pkg in (new, dict(new)):
            packages.update(new_pkg)  # Should now be identical
            self.assertDictEqual(packages.difference(new_pkg), {})
            self.assertDictEqual(packages.missing(new_pkg), {})
            self.assertDictEqual(packages.extra(new_pkg), {})
            self.assertEqual(len(packages), len(new_pkg))

        # Loop over keys to check iterator.
        keys = {k for k in new}
        self.assertEqual(keys, set(dict(new).keys()))

        # Loop over values to check that we do get them all.
        values = {v for v in new.values()}
        self.assertEqual(values, set(dict(new).values()))

        # Serialize via bytes
        for format in ("pickle", "yaml", "json"):
            asbytes = new.toBytes(format)
            from_bytes = lsst.utils.packages.Packages.fromBytes(asbytes, format)
            self.assertEqual(from_bytes, new)

        with self.assertRaises(ValueError):
            new.toBytes("unknown_format")

        with self.assertRaises(ValueError):
            lsst.utils.packages.Packages.fromBytes(from_bytes, "unknown_format")

        with self.assertRaises(TypeError):
            some_yaml = b"list: [1, 2]"
            lsst.utils.packages.Packages.fromBytes(some_yaml, "yaml")

    def testBackwardsCompatibility(self):
        """Test if we can read old data files."""

        # Pickle contents changed when moving to dict base class.
        packages_p = lsst.utils.packages.Packages.read(os.path.join(TESTDIR, "data", "v1.pickle"))
        self.assertIsInstance(packages_p, lsst.utils.packages.Packages)

        # YAML format is unchanged when moving from special class to dict
        # but test anyway.
        packages_y = lsst.utils.packages.Packages.read(os.path.join(TESTDIR, "data", "v1.yaml"))

        self.assertEqual(packages_p, packages_y)

        # Now check that we can read the version 2 files that were
        # written with Packages inheriting from dict but still in `base`.
        packages_p2 = lsst.utils.packages.Packages.read(os.path.join(TESTDIR, "data", "v2.pickle"))
        packages_y2 = lsst.utils.packages.Packages.read(os.path.join(TESTDIR, "data", "v2.yaml"))
        self.assertEqual(packages_p2, packages_y2)
        self.assertIsInstance(packages_p2, lsst.utils.packages.Packages)


if __name__ == "__main__":
    unittest.main()
