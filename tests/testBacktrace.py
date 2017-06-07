#
# LSST Data Management System
# Copyright 2008-2016 LSST Corporation.
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
import sys
import unittest
import subprocess

import lsst.utils.tests
from lsst.utils import backtrace


class BacktraceTestCase(lsst.utils.tests.TestCase):
    def setUp(self):
        pass

    def test_segfault(self):
        if backtrace.isEnabled():
            pipe = subprocess.Popen((sys.executable, "tests/backtrace.py"),
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)

            found = False
            for l in pipe.stderr:
                if "backtrace follows" in str(l):
                    found = True
                    break
            self.assertTrue(found)


class TestMemory(lsst.utils.tests.MemoryTestCase):
    pass


def setup_module(module):
    lsst.utils.tests.init()


if __name__ == "__main__":
    setup_module(sys.modules[__name__])
    unittest.main()
