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

try:
    import numexpr
except ImportError:
    numexpr = None
try:
    import threadpoolctl
except ImportError:
    threadpoolctl = None


class ThreadsTestCase(unittest.TestCase):
    """Tests for threads."""

    def testDisable(self):
        set_thread_envvars(2, override=True)
        self.assertEqual(os.environ["OMP_NUM_THREADS"], "2")
        set_thread_envvars(3, override=False)
        self.assertEqual(os.environ["OMP_NUM_THREADS"], "2")

        disable_implicit_threading()
        self.assertEqual(os.environ["OMP_NUM_THREADS"], "1")

        # Check that we have only one thread.
        if numexpr:
            self.assertEqual(numexpr.utils.get_num_threads(), 1)
        if threadpoolctl:
            info = threadpoolctl.threadpool_info()
            for api in info:
                self.assertEqual(api["num_threads"], 1, f"API: {api}")


if __name__ == "__main__":
    unittest.main()
