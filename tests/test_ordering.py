#
# LSST Data Management System
# Copyright 2016 LSST Corporation.
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
# see <http://www.lsstcorp.org/LegalNotices/>.
#
import unittest
import lsst.utils.tests


class TestCaseOrdering(lsst.utils.tests.TestCase):
    def testTestOrdering(self):
        class DummyTest(lsst.utils.tests.TestCase):
            def noOp(self):
                pass

        class DummyMemoryTest(lsst.utils.tests.MemoryTestCase):
            pass

        class DummyTest2(unittest.TestCase):
            def noOp(self):
                pass

        suite = unittest.defaultTestLoader.suiteClass([DummyTest2("noOp"), DummyMemoryTest("testLeaks"),
                                                       DummyTest("noOp")])

        self.assertNotIsInstance(suite._tests[0], lsst.utils.tests.MemoryTestCase)
        self.assertIsInstance(suite._tests[-1], lsst.utils.tests.MemoryTestCase)


if __name__ == "__main__":
    unittest.main()
