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

import datetime
import logging
import os.path
import pstats
import tempfile
import time
import unittest
from dataclasses import dataclass

from astropy import units as u
from lsst.utils.timer import logInfo, logPairs, profile, time_this, timeMethod

log = logging.getLogger("test_timer")

THIS_FILE = os.path.basename(__file__)

# Only use this in a single test but needs to be associated
# with the function up front.
test_metadata = {}


@dataclass
class Example1:
    log: logging.Logger
    metadata: dict

    @timeMethod
    def sleeper(self, duration: float) -> None:
        """Sleep for some time."""
        time.sleep(duration)


@timeMethod
def decorated_sleeper_nothing(self, duration: float) -> None:
    time.sleep(duration)


@timeMethod(logger=log)
def decorated_sleeper_logger(self, duration: float) -> None:
    time.sleep(duration)


@timeMethod(logger=log, logLevel=logging.INFO)
def decorated_sleeper_logger_level(self, duration: float) -> None:
    time.sleep(duration)


@timeMethod(metadata=test_metadata)
def decorated_sleeper_metadata(self, duration: float) -> None:
    time.sleep(duration)


class TestTimeMethod(unittest.TestCase):
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


class TimerTestCase(unittest.TestCase):
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
        with self.assertLogs(level="ERROR") as cm:
            with self.assertRaises(RuntimeError):
                with time_this(log=logging.getLogger(logname), prefix=prefix):
                    raise RuntimeError("A problem")
        self.assertEqual(cm.records[0].name, f"{prefix}.{logname}")
        self.assertEqual(cm.records[0].levelname, "ERROR")


class ProfileTestCase(unittest.TestCase):
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
            self.assertIsInstance(pstats.Stats(tmp.name), pstats.Stats),


if __name__ == "__main__":
    unittest.main()
