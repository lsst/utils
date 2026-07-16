# This file is part of utils.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
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
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import unittest
import unittest.mock

from lsst.utils.threads import disable_implicit_threading, set_thread_envvars

try:
    import numexpr
except ImportError:
    numexpr = None
try:
    import threadpoolctl
except ImportError:
    threadpoolctl = None
try:
    import pyarrow
except ImportError:
    pyarrow = None
try:
    import numba
except ImportError:
    numba = None


class ThreadsTestCase(unittest.TestCase):
    """Tests for threads."""

    def testDisable(self):
        set_thread_envvars(2, override=True)
        self.assertEqual(os.environ["OMP_NUM_THREADS"], "2")
        set_thread_envvars(3, override=False)
        self.assertEqual(os.environ["OMP_NUM_THREADS"], "2")

        disable_implicit_threading()
        self.assertEqual(os.environ["OMP_NUM_THREADS"], "1")
        self.assertEqual(os.environ["OMP_PROC_BIND"], "false")

        # Check that we have only one thread.
        if numexpr:
            self.assertEqual(numexpr.utils.get_num_threads(), 1)
        if threadpoolctl:
            info = threadpoolctl.threadpool_info()
            for api in info:
                self.assertEqual(api["num_threads"], 1, f"API: {api}")

    def testEnvVarsForEnvOnlyLibraries(self):
        """Libraries that are only controllable via environment variables
        must be included in the list of variables that are set.
        """
        set_thread_envvars(2, override=True)
        for var in (
            "NUMBA_NUM_THREADS",
            "ARROW_IO_THREADS",
            "VECLIB_MAXIMUM_THREADS",
            "RAYON_NUM_THREADS",
            "POLARS_MAX_THREADS",
            "BLIS_NUM_THREADS",
        ):
            self.assertEqual(os.environ.get(var), "2", f"Variable: {var}")

    @unittest.skipIf(pyarrow is None, "pyarrow is not available")
    def testDisablePyarrow(self):
        """Already-created pyarrow thread pools must be resized since they
        do not react to environment variables after creation.
        """
        pyarrow.set_cpu_count(4)
        pyarrow.set_io_thread_count(4)
        disable_implicit_threading()
        self.assertEqual(pyarrow.cpu_count(), 1)
        self.assertEqual(pyarrow.io_thread_count(), 1)

    @unittest.skipIf(numba is None, "numba is not available")
    def testDisableNumba(self):
        """An already-imported numba must be limited at runtime since it
        reads its environment variable only at import time.
        """
        if numba.config.NUMBA_NUM_THREADS > 1:
            numba.set_num_threads(2)
        disable_implicit_threading()
        self.assertEqual(numba.get_num_threads(), 1)

    @unittest.skipIf(threadpoolctl is None, "threadpoolctl is not available")
    def testMissingThreadpoolctlWarning(self):
        """Absence of threadpoolctl silently weakens the thread disabling
        so it must be reported.
        """
        with (
            unittest.mock.patch("lsst.utils.threads.threadpool_limits", None),
            self.assertLogs("lsst.utils.threads", "WARNING") as cm,
        ):
            disable_implicit_threading()
        self.assertIn("threadpoolctl", "\n".join(cm.output))


if __name__ == "__main__":
    unittest.main()
