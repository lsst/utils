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
import os
import sys
import unittest
import time
import threading

from lsst.utils.multithreading import SharedData

class ShareDataTestCase(unittest.TestCase):

    def setUp(self):
        self.sd = SharedData()

    def tearDown(self):
        pass

    def testCtor(self):
        pass

    def testAcquire(self):
        self.assert_(not self.sd._is_owned(), "lock without acquire")
        self.sd.acquire()
        self.assert_(self.sd._is_owned(), "lock not acquired")
        self.sd.acquire()
        self.assert_(self.sd._is_owned(), "lock not kept")
        self.sd.release()
        self.assert_(self.sd._is_owned(),"lock not kept after partial release")
        self.sd.release()
        self.assert_(not self.sd._is_owned(), "lock not released")

    def testNoData(self):
        attrs = self.sd.dir()
        self.assertEquals(len(attrs), 0,
                          "Non-empty protected dir: " + str(attrs))
        self.sd.acquire()
        self.assert_(self.sd.__, "__ not set")
        self.sd.release()

    def testWith(self):
        with self.sd:
            self.assert_(self.sd._is_owned(), "lock not acquired")
        self.assert_(not self.sd._is_owned(), "lock not released")

    def _initData(self):
        self.sd.initData({ "name": "Ray", "test": True, "config": {} })

    def testNoLockRead(self):
        self._initData()
        try:
            self.sd.name
            self.fail("AttributeError not raised for reading w/o lock ")
        except AttributeError, e:
            pass
        self.sd.dir()

    def testInit(self):
        self._initData()
        attrs = self.sd.dir()
        self.assertEquals(len(attrs), 3, "Wrong number of items: "+str(attrs))
        for key in "name test config".split():
            self.assert_(key in attrs, "Missing attr: " + key)

    def testAccess(self):
        self._initData()
        protected = None
        with self.sd:
            self.assertEquals(self.sd.name, "Ray")
            self.assert_(isinstance(self.sd.test, bool))
            self.assert_(self.sd.test)
            protected = self.sd.config
            self.assert_(isinstance(protected, dict))
            self.assertEquals(len(protected), 0)

        # test unsafe access
        protected["goob"] = "gurn"
        with self.sd:
            self.assertEquals(self.sd.config["goob"], "gurn")

    def testUpdate(self):
        self._initData()
        with self.sd:
            self.sd.name = "Plante"
            self.assertEquals(self.sd.name, "Plante")
        attrs = self.sd.dir()
        self.assertEquals(len(attrs), 3, "Wrong number of items: "+str(attrs))
            
    def testAdd(self):
        self._initData()
        with self.sd:
            self.sd.lname = "Plante"
            attrs = self.sd.dir()
            self.assertEquals(len(attrs), 4, "Wrong number of items: "+str(attrs))
            self.assertEquals(self.sd.lname, "Plante")
            
class ReadableShareDataTestCase(unittest.TestCase):

    def setUp(self):
        self.sd = SharedData(False)

    def tearDown(self):
        pass

    def testAcquire(self):
        self.assert_(not self.sd._is_owned(), "lock without acquire")
        self.sd.acquire()
        self.assert_(self.sd._is_owned(), "lock not acquired")
        self.sd.acquire()
        self.assert_(self.sd._is_owned(), "lock not kept")
        self.sd.release()
        self.assert_(self.sd._is_owned(),"lock not kept after partial release")
        self.sd.release()
        self.assert_(not self.sd._is_owned(), "lock not released")

    def testNoData(self):
        attrs = self.sd.dir()
        self.assertEquals(len(attrs), 0,
                          "Non-empty protected dir: " + str(attrs))
        self.assert_(self.sd.__, "__ not set")

    def _initData(self):
        self.sd.initData({ "name": "Ray", "test": True, "config": {} })

    def testNoLockRead(self):
        self._initData()
        self.sd.name
        self.sd.dir()
        try:
            self.sd.goob
            self.fail("AttributeError not raised for accessing non-existent")
        except AttributeError, e:
            pass

    def testInit(self):
        self._initData()
        attrs = self.sd.dir()
        self.assertEquals(len(attrs), 3, "Wrong number of items: "+str(attrs))
        for key in "name test config".split():
            self.assert_(key in attrs, "Missing attr: " + key)

    def testAccess(self):
        self._initData()
        protected = None

        self.assertEquals(self.sd.name, "Ray")
        self.assert_(isinstance(self.sd.test, bool))
        self.assert_(self.sd.test)
        protected = self.sd.config
        self.assert_(isinstance(protected, dict))
        self.assertEquals(len(protected), 0)

        # test unsafe access
        protected["goob"] = "gurn"
        self.assertEquals(self.sd.config["goob"], "gurn")

    def testUpdate(self):
        self._initData()
        with self.sd:
            self.sd.name = "Plante"
            self.assertEquals(self.sd.name, "Plante")
        attrs = self.sd.dir()
        self.assertEquals(len(attrs), 3, "Wrong number of items: "+str(attrs))
            
    def testAdd(self):
        self._initData()
        with self.sd:
            self.sd.lname = "Plante"
            attrs = self.sd.dir()
            self.assertEquals(len(attrs), 4, "Wrong number of items: "+str(attrs))
            self.assertEquals(self.sd.lname, "Plante")

class MultiThreadTestCase(unittest.TestCase):
    
    def setUp(self):
        self.sd = SharedData(False, { "c": 0 })

    def tearDown(self):
        pass

    def testThreads(self):
        t = TstThread(self.sd)
        # pdb.set_trace()
        self.assertEquals(self.sd.c, 0)
        # print "c = ", self.sd.c
        
        with self.sd:
            t.start()

            # now take a turn
            self.sd.wait()
            # print "c = ", self.sd.c
            self.assertEquals(self.sd.c, 1)
            # print "WILL NOTIFY"
            self.sd.notifyAll()

        # time.sleep(1.01)
        with self.sd:
            # print "WILL WAIT"
            self.sd.wait(2.0)
            self.assertEquals(self.sd.c, 0)

        

class TstThread(threading.Thread):

    def __init__(self, data):
        threading.Thread.__init__(self)
        self.data = data

    def run(self):
        with self.data:
            # pdb.set_trace()
            self.data.c += 1
            # print "++c = ", self.data.c

            self.data.notifyAll()
            # print "waiting", self.data.c
            self.data.wait()

            self.data.c -= 1
            # print "--c = ", self.data.c
            self.data.notifyAll()


    

__all__ = "SharedDataTestCase ReadableShareDataTestCase MultiThreadTestCase".split()        

if __name__ == "__main__":
    unittest.main()

    
