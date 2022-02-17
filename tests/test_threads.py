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

from lsst.utils.threads import disable_implicit_threading, set_thread_envvars


class ThreadsTestCase(unittest.TestCase):
    """Tests for threads."""

    def testDisable(self):
        set_thread_envvars(2, override=True)
        self.assertEqual(os.environ["OMP_NUM_THREADS"], "2")
        set_thread_envvars(3, override=False)
        self.assertEqual(os.environ["OMP_NUM_THREADS"], "2")

        disable_implicit_threading()
        self.assertEqual(os.environ["OMP_NUM_THREADS"], "1")


if __name__ == "__main__":
    unittest.main()
