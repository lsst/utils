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

import datetime
import logging
import os
import os.path
import pstats
import tempfile
import time
import unittest
from dataclasses import dataclass

from astropy import units as u

from lsst.utils.timer import duration_from_timeMethod, logInfo, logPairs, profile, time_this, timeMethod

log = logging.getLogger("test_timer")

THIS_FILE = os.path.basename(__file__)

# Only use this in a single test but needs to be associated
# with the function up front.
test_metadata = {}


@dataclass
class Example1:
    """Test class with log and metadata properties, similar to ``Task``."""

    log: logging.Logger
    metadata: dict

    @timeMethod
    def sleeper(self, duration: float) -> None:
        """Sleep for some time."""
        time.sleep(duration)


@timeMethod
def decorated_sleeper_nothing(self, duration: float) -> None:
    """Test function that sleeps."""
    time.sleep(duration)


@timeMethod(logger=log)
def decorated_sleeper_logger(self, duration: float) -> None:
    """Test function that sleeps and logs."""
    time.sleep(duration)


@timeMethod(logger=log, logLevel=logging.INFO)
def decorated_sleeper_logger_level(self, duration: float) -> None:
    """Test function that logs at INFO."""
    time.sleep(duration)


@timeMethod(metadata=test_metadata)
def decorated_sleeper_metadata(self, duration: float) -> None:
    """Test function that uses external metadata."""
    time.sleep(duration)


class TestTimeMethod(unittest.TestCase):
    """Test the time method decorator."""

    def testLogPairs(self):
        # Test the non-obj case.
        logger = logging.getLogger("test")
        pairs = (("name1", 0), ("name2", 1))
        metadata = {}
        with self.assertLogs(level=logging.INFO) as cm:
            logPairs(None, pairs, logLevel=logging.INFO, logger=logger, metadata=metadata)
        self.assertEqual(len(cm.output), 1, cm.output)
        self.assertTrue(cm.output[0].endswith("name1=0; name2=1"), cm.output)
        self.assertEqual(cm.records[0].filename, THIS_FILE, "log message should originate from here")
        self.assertEqual(metadata, {"name1": [0], "name2": [1]})

        # Call it again with an explicit stack level.
        # Force it to come from lsst.utils.
        with self.assertLogs(level=logging.INFO) as cm:
            logPairs(None, pairs, logLevel=logging.INFO, logger=logger, metadata=metadata, stacklevel=0)
        self.assertEqual(cm.records[0].filename, "timer.py")

        # Check that the log message is filtered by default.
        with self.assertLogs(level=logging.INFO) as cm:
            logPairs(None, pairs, logger=logger, metadata=metadata)
            logger.info("Message")
        self.assertEqual(len(cm.records), 1)

    def testLogInfo(self):
        metadata = {}
        logger = logging.getLogger("testLogInfo")
        with self.assertLogs(level=logging.INFO) as cm:
            logInfo(None, prefix="Prefix", metadata=metadata, logger=logger, logLevel=logging.INFO)
        self.assertEqual(cm.records[0].filename, THIS_FILE)
        self.assertIn("PrefixUtc", metadata)
        self.assertIn("PrefixMaxResidentSetSize", metadata)
        self.assertIn("nodeName", metadata)
        self.assertEqual(metadata["__version__"], 1)

        # Again with no log output.
        logInfo(None, prefix="Prefix", metadata=metadata)
        self.assertEqual(len(metadata["PrefixUtc"]), 2)

        # With an explicit stacklevel.
        with self.assertLogs(level=logging.INFO) as cm:
            logInfo(
                None, prefix="Prefix", metadata=metadata, logger=logger, logLevel=logging.INFO, stacklevel=0
            )
        self.assertEqual(cm.records[0].filename, "timer.py")

    def assertTimer(self, duration, task):
        # Call it twice to test the "add" functionality.
        task.sleeper(duration)
        task.sleeper(duration)
        counter = 2

        has_logger = getattr(task, "log", None) is not None and task.log is not None
        has_metadata = getattr(task, "metadata", None) is not None and task.metadata is not None

        if has_logger:
            counter += 1
            with self.assertLogs("timer.task", level=logging.DEBUG) as cm:
                task.sleeper(duration)
            self.assertEqual(cm.records[0].filename, THIS_FILE, "log message should originate from here")

        if has_metadata:
            self.assertEqual(len(task.metadata["sleeperStartUserTime"]), counter)

            start = datetime.datetime.fromisoformat(task.metadata["sleeperStartUtc"][1])
            end = datetime.datetime.fromisoformat(task.metadata["sleeperEndUtc"][1])
            delta = end - start
            delta_sec = delta.seconds + (delta.microseconds / 1e6)
            self.assertGreaterEqual(delta_sec, duration)

    def testTaskLike(self):
        """Test timer on something that looks like a Task."""
        # Call with different parameters.
        parameters = (
            (logging.getLogger("task"), {}),
            (logging.getLogger("task"), None),
            (None, {}),
            (None, None),
        )

        duration = 0.1
        for log, metadata in parameters:
            with self.subTest(log=log, metadata=metadata):
                task = Example1(log=log, metadata=metadata)
                self.assertTimer(duration, task)
                exampleDuration = duration_from_timeMethod(task.metadata, "sleeper")
                if metadata is not None:
                    self.assertGreater(exampleDuration, 0)

    def testDecorated(self):
        """Test timeMethod on non-Task like instances."""
        duration = 0.1

        # The "self" object shouldn't be usable but this should do nothing
        # and not crash.
        decorated_sleeper_nothing(self, duration)

        # Use a function decorated for logging.
        with self.assertLogs("timer.test_timer", level=logging.DEBUG) as cm:
            decorated_sleeper_logger(self, duration)
        self.assertEqual(cm.records[0].filename, THIS_FILE, "log message should originate from here")

        # And adjust the log level
        with self.assertLogs("timer.test_timer", level=logging.INFO):
            decorated_sleeper_logger_level(self, duration)

        # Use a function decorated for metadata.
        self.assertEqual(len(test_metadata), 0)
        with self.assertLogs("timer.test_timer", level=logging.DEBUG) as cm:
            # Check that we only get a single log message and nothing from
            # timeMethod itself.
            decorated_sleeper_metadata(self, duration)
            logging.getLogger("timer.test_timer").debug("sentinel")
        self.assertEqual(len(cm.output), 1)
        self.assertIn("decorated_sleeper_metadataStartUserTime", test_metadata)

    def testDisabled(self):
        """Test that setting the appropriate envvar disables the decorator."""
        duration = 0.1

        with unittest.mock.patch.dict(os.environ, {"LSST_UTILS_DISABLE_TIMER": "1"}, clear=True):
            import decorator_test.disable_timer

            # For an empty decorator, we have to check for the attribute that
            # `functools.wraps` attaches to the function.
            self.assertFalse(hasattr(decorator_test.disable_timer.sleep_and_nothing, "__wrapped__"))

            # For a decorator with kwargs, no logs should be emitted.
            with self.assertNoLogs("timer.disable_timer", level=logging.INFO):
                decorator_test.disable_timer.sleep_and_log(self, duration)


class TimerTestCase(unittest.TestCase):
    """Test the timer functionality."""

    def testTimer(self):
        with self.assertLogs(level="DEBUG") as cm:
            with time_this():
                pass
        self.assertEqual(cm.records[0].name, "timer")
        self.assertEqual(cm.records[0].levelname, "DEBUG")
        self.assertEqual(cm.records[0].filename, THIS_FILE)

        with self.assertLogs(level="DEBUG") as cm:
            with time_this(prefix=None):
                pass
        self.assertEqual(cm.records[0].name, "root")
        self.assertEqual(cm.records[0].levelname, "DEBUG")
        self.assertIn("Took", cm.output[0])
        self.assertNotIn(": Took", cm.output[0])
        self.assertNotIn("; ", cm.output[0])
        self.assertEqual(cm.records[0].filename, THIS_FILE)

        # Report memory usage.
        with self.assertLogs(level="DEBUG") as cm:
            with time_this(level=logging.DEBUG, prefix=None, mem_usage=True):
                pass
        self.assertEqual(cm.records[0].name, "root")
        self.assertEqual(cm.records[0].levelname, "DEBUG")
        self.assertIn("Took", cm.output[0])
        self.assertIn("memory", cm.output[0])
        self.assertIn("delta", cm.output[0])
        self.assertIn("peak delta", cm.output[0])
        self.assertIn("byte", cm.output[0])

        # Request memory usage but with log level that will not issue it.
        with self.assertLogs(level="INFO") as cm:
            with time_this(level=logging.DEBUG, prefix=None, mem_usage=True):
                pass
            # Ensure that a log message is issued.
            _log = logging.getLogger()
            _log.info("info")
        self.assertEqual(cm.records[0].name, "root")
        self.assertEqual(cm.records[0].levelname, "INFO")
        all = "\n".join(cm.output)
        self.assertNotIn("Took", all)
        self.assertNotIn("memory", all)

        # Report memory usage including child processes.
        with self.assertLogs(level="DEBUG") as cm:
            with time_this(level=logging.DEBUG, prefix=None, mem_usage=True, mem_child=True):
                pass
        self.assertEqual(cm.records[0].name, "root")
        self.assertEqual(cm.records[0].levelname, "DEBUG")
        self.assertIn("Took", cm.output[0])
        self.assertIn("memory", cm.output[0])
        self.assertIn("delta", cm.output[0])
        self.assertIn("peak delta", cm.output[0])
        self.assertIn("byte", cm.output[0])

        # Report memory usage, use non-default, but a valid memory unit.
        with self.assertLogs(level="DEBUG") as cm:
            with time_this(level=logging.DEBUG, prefix=None, mem_usage=True, mem_unit=u.kilobyte):
                pass
        self.assertEqual(cm.records[0].name, "root")
        self.assertEqual(cm.records[0].levelname, "DEBUG")
        self.assertIn("Took", cm.output[0])
        self.assertIn("memory", cm.output[0])
        self.assertIn("delta", cm.output[0])
        self.assertIn("peak delta", cm.output[0])
        self.assertIn("kbyte", cm.output[0])

        # Report memory usage, use an invalid memory unit.
        with self.assertLogs(level="DEBUG") as cm:
            with time_this(level=logging.DEBUG, prefix=None, mem_usage=True, mem_unit=u.gram):
                pass
        self.assertEqual(cm.records[0].name, "lsst.utils.timer")
        self.assertEqual(cm.records[0].levelname, "WARNING")
        self.assertIn("Invalid", cm.output[0])
        self.assertIn("byte", cm.output[0])
        self.assertEqual(cm.records[1].name, "root")
        self.assertEqual(cm.records[1].levelname, "DEBUG")
        self.assertIn("Took", cm.output[1])
        self.assertIn("memory", cm.output[1])
        self.assertIn("delta", cm.output[1])
        self.assertIn("peak delta", cm.output[1])
        self.assertIn("byte", cm.output[1])

        # Change logging level
        with self.assertLogs(level="INFO") as cm:
            with time_this(level=logging.INFO, prefix=None):
                pass
        self.assertEqual(cm.records[0].name, "root")
        self.assertIn("Took", cm.output[0])
        self.assertIn("seconds", cm.output[0])

        # Use a new logger with a message.
        msg = "Test message %d"
        test_num = 42
        logname = "test"
        with self.assertLogs(level="DEBUG") as cm:
            with time_this(log=logging.getLogger(logname), msg=msg, args=(42,), prefix=None):
                pass
        self.assertEqual(cm.records[0].name, logname)
        self.assertIn("Took", cm.output[0])
        self.assertIn(msg % test_num, cm.output[0])

        # Prefix the logger.
        prefix = "prefix"
        with self.assertLogs(level="DEBUG") as cm:
            with time_this(prefix=prefix):
                pass
        self.assertEqual(cm.records[0].name, prefix)
        self.assertIn("Took", cm.output[0])

        # Prefix explicit logger.
        with self.assertLogs(level="DEBUG") as cm:
            with time_this(log=logging.getLogger(logname), prefix=prefix):
                pass
        self.assertEqual(cm.records[0].name, f"{prefix}.{logname}")

        # Trigger a problem.
        with self.assertLogs(level="DEBUG") as cm:
            with self.assertRaises(RuntimeError):
                with time_this(log=logging.getLogger(logname), prefix=prefix):
                    raise RuntimeError("A problem %s")
        self.assertEqual(cm.records[0].name, f"{prefix}.{logname}")
        self.assertIn("A problem %s", cm.records[0].message)
        self.assertEqual(cm.records[0].levelname, "DEBUG")

    def test_time_this_return(self):
        """Test that the context manager returns the duration."""
        # Return duration but not memory usage.
        with self.assertNoLogs(level="INFO"):
            with time_this(level=logging.DEBUG, prefix=None, mem_usage=False) as timer:
                time.sleep(0.01)
        self.assertGreater(timer.duration, 0.0)
        self.assertIsNone(timer.mem_current_usage)

        # Ask for memory usage that will be calculated.
        with self.assertLogs(level="DEBUG"):
            # mem usage will be requested but not calculated.
            with time_this(level=logging.DEBUG, prefix=None, mem_usage=True) as timer:
                time.sleep(0.01)
        self.assertGreater(timer.duration, 0.0)
        self.assertGreaterEqual(timer.mem_current_delta, 0.0)

        # Ask for memory usage but will not be calculated.
        with self.assertNoLogs(level="WARNING"):
            # mem usage will be requested but not calculated.
            with time_this(level=logging.DEBUG, prefix=None, mem_usage=True) as timer:
                time.sleep(0.01)
        self.assertGreater(timer.duration, 0.0)
        self.assertIsNone(timer.mem_current_usage)

        # Require memory usage is returned in context manager.
        with self.assertNoLogs(level="WARNING"):
            with time_this(level=logging.DEBUG, prefix=None, force_mem_usage=True) as timer:
                time.sleep(0.01)
        self.assertGreater(timer.duration, 0.0)
        self.assertGreater(timer.mem_current_usage, 0.0)


class ProfileTestCase(unittest.TestCase):
    """Test profiling decorator."""

    def test_profile(self):
        logger = logging.getLogger("profile")

        with profile(None) as prof:
            pass
        self.assertIsNone(prof)

        with tempfile.NamedTemporaryFile() as tmp:
            with self.assertLogs("profile", level=logging.INFO) as cm:
                with profile(tmp.name, logger) as prof:
                    pass
            self.assertEqual(len(cm.output), 2)
            self.assertIsNotNone(prof)
            self.assertTrue(os.path.exists(tmp.name))
            self.assertIsInstance(pstats.Stats(tmp.name), pstats.Stats)


if __name__ == "__main__":
    unittest.main()
