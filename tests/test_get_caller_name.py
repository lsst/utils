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

import sys
import unittest

import lsst.utils.tests
from lsst.utils import get_caller_name


class GetCallerNameTestCase(unittest.TestCase):
    """Test get_caller_name

    Warning: due to the different ways this can be run
    (e.g. directly or py.test), the module name can be one of two different
    things.
    """

    def test_free_function(self):
        def test_func():
            return get_caller_name(1)

        result = test_func()
        self.assertEqual(result, "{}.test_func".format(__name__))

    def test_instance_method(self):
        class TestClass:
            def run(self):
                return get_caller_name(1)

        tc = TestClass()
        result = tc.run()
        self.assertEqual(result, "{}.TestClass.run".format(__name__))

    def test_class_method(self):
        class TestClass:
            @classmethod
            def run(cls):
                return get_caller_name(1)

        tc = TestClass()
        result = tc.run()
        self.assertEqual(result, "{}.TestClass.run".format(__name__))

    def test_skip(self):
        def test_func(skip):
            return get_caller_name(skip)

        result = test_func(2)
        self.assertEqual(result, "{}.GetCallerNameTestCase.test_skip".format(__name__))

        result = test_func(2000000)  # use a large number to avoid details of how the test is run
        self.assertEqual(result, "")


def setup_module(module):
    lsst.utils.tests.init()


if __name__ == "__main__":
    setup_module(sys.modules[__name__])
    unittest.main()
