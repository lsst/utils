#!/usr/bin/env python
#
# LSST Data Management System
# Copyright 2016 AURA/LSST.
#
# This product includes software developed by the
# LSST Project (http://www.lsst.org/).
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
# You should have received a copy of the LSST License Statement and
# the GNU General Public License along with this program.  If not,
# see <https://www.lsstcorp.org/LegalNotices/>.
#
import os
import unittest
import tempfile

import lsst.base

from future import standard_library
standard_library.install_aliases()


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
        versions = lsst.base.getPythonPackages()
        expected = (lsst.base.version.__version__)
        self.assertEqual(versions["base"], expected)

    def testEnvironment(self):
        """Test getting versions from the environment

        Unfortunately, none of the products that need their versions divined from the
        environment are dependencies of this package, and so all we can do is test
        that this doesn't fall over.
        """
        lsst.base.getEnvironmentPackages()

    def testRuntime(self):
        """Test getting versions from runtime libraries

        Unfortunately, none of the products that we get runtime versions from are
        dependencies of this package, and so all we can do is test that this doesn't
        fall over.
        """
        lsst.base.getRuntimeVersions()

    def testPackages(self):
        """Test the Packages class"""
        packages = lsst.base.Packages.fromSystem()

        # Test pickling
        # Can't use lsst.utils.tests.getTempFilePath because we're its dependency
        temp = tempfile.NamedTemporaryFile(prefix="packages.", suffix=".pickle", delete=False)
        tempName = temp.name
        temp.close()  # We don't use the fd, just want a filename
        try:
            packages.write(tempName)
            new = lsst.base.Packages.read(tempName)
        finally:
            os.unlink(tempName)

        # 'packages' and 'new' should have identical content
        self.assertDictEqual(packages.difference(new), {})
        self.assertDictEqual(packages.missing(new), {})
        self.assertDictEqual(packages.extra(new), {})
        self.assertEqual(len(packages), len(new))

        # Check inverted comparisons
        self.assertDictEqual(new.difference(packages), {})
        self.assertDictEqual(new.missing(packages), {})
        self.assertDictEqual(new.extra(packages), {})

        # Now load an obscure python package and the list of packages should change
        import smtpd  # noqa Shouldn't be used by anything we've previously imported
        new = lsst.base.Packages.fromSystem()
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

        packages.update(new)  # Should now be identical
        self.assertDictEqual(packages.difference(new), {})
        self.assertDictEqual(packages.missing(new), {})
        self.assertDictEqual(packages.extra(new), {})
        self.assertEqual(len(packages), len(new))


if __name__ == "__main__":
    unittest.main()
