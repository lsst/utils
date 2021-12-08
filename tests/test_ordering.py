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

        suite = unittest.defaultTestLoader.suiteClass(
            [DummyTest2("noOp"), DummyMemoryTest("testFileDescriptorLeaks"), DummyTest("noOp")]
        )

        self.assertNotIsInstance(suite._tests[0], lsst.utils.tests.MemoryTestCase)
        self.assertIsInstance(suite._tests[-1], lsst.utils.tests.MemoryTestCase)


if __name__ == "__main__":
    unittest.main()
