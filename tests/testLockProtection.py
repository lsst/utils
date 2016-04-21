#!/usr/bin/env python

#
# LSST Data Management System
# Copyright 2008, 2009, 2010 LSST Corporation.
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

"""
Tests of the SharedData class
"""
from __future__ import with_statement

import pdb                              # we may want to say pdb.set_trace()
import unittest

from lsst.utils.multithreading import *


class MyClass(LockProtected):

    def __init__(self, lock=None):
        LockProtected.__init__(self, lock)

    def danger(self):
        self._checkLocked()

    def fail(self):
        self._checkLocked()
        raise RuntimeError()


class LockProtectedTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testNoLock(self):
        mc = MyClass()
        mc.danger()
        with mc:
            mc.danger()

    def testSharedLock(self):
        mc = MyClass(SharedLock())
        self.assertRaises(UnsafeAccessError, mc.danger)
        with mc:
            mc.danger()

    def testSharedData(self):
        mc = MyClass(SharedData())
        self.assertRaises(UnsafeAccessError, mc.danger)
        with mc:
            mc.danger()

    def testExitViaException(self):
        mc = MyClass(SharedLock())
        with mc:
            self.assertRaises(RuntimeError, mc.fail)

__all__ = "LockProtectedTestCase".split()

if __name__ == "__main__":
    unittest.main()
