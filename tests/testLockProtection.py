#!/usr/bin/env python
"""
Tests of the SharedData class
"""
from __future__ import with_statement

import pdb                              # we may want to say pdb.set_trace()
import os
import sys
import unittest
import time

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

