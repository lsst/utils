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

import unittest
import logging
import time
import datetime
from dataclasses import dataclass

from lsst.utils.timer import timeMethod, logPairs, time_this

log = logging.getLogger("test_timer")

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
        self.assertEqual(metadata, {"name1": [0], "name2": [1]})

    def assertTimer(self, duration, task):
        # Call it twice to test the "add" functionality.
        task.sleeper(duration)
        task.sleeper(duration)
        counter = 2

        has_logger = getattr(task, "log", None) is not None \
            and task.log is not None
        has_metadata = getattr(task, "metadata", None) is not None \
            and task.metadata is not None

        if has_logger:
            counter += 1
            with self.assertLogs("timer.task", level=logging.DEBUG):
                task.sleeper(duration)

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
        parameters = ((logging.getLogger("task"), {}),
                      (logging.getLogger("task"), None),
                      (None, {}),
                      (None, None))

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
        with self.assertLogs("timer.test_timer", level=logging.DEBUG):
            decorated_sleeper_logger(self, duration)

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
        self.assertEqual(cm.records[0].filename, "test_timer.py")

        with self.assertLogs(level="DEBUG") as cm:
            with time_this(prefix=None):
                pass
        self.assertEqual(cm.records[0].name, "root")
        self.assertEqual(cm.records[0].levelname, "DEBUG")
        self.assertIn("Took", cm.output[0])
        self.assertEqual(cm.records[0].filename, "test_timer.py")

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
            with time_this(log=logging.getLogger(logname),
                           msg=msg, args=(42,), prefix=None):
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
            with time_this(log=logging.getLogger(logname),
                           prefix=prefix):
                pass
        self.assertEqual(cm.records[0].name, f"{prefix}.{logname}")

        # Trigger a problem.
        with self.assertLogs(level="ERROR") as cm:
            with self.assertRaises(RuntimeError):
                with time_this(log=logging.getLogger(logname),
                               prefix=prefix):
                    raise RuntimeError("A problem")
        self.assertEqual(cm.records[0].name, f"{prefix}.{logname}")
        self.assertEqual(cm.records[0].levelname, "ERROR")


if __name__ == "__main__":
    unittest.main()