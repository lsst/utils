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

import logging
import time
import unittest

from lsst.utils.logging import LogState, PeriodicLogger, getLogger, trace_set_at


class TestLogging(unittest.TestCase):
    """Simple unit tests for Task logging."""

    def testLogLevels(self):
        """Check that the new log levels look reasonable."""
        root = getLogger()

        self.assertEqual(root.DEBUG, logging.DEBUG)
        self.assertGreater(root.VERBOSE, logging.DEBUG)
        self.assertLess(root.VERBOSE, logging.INFO)
        self.assertLess(root.TRACE, logging.DEBUG)

    def testLogCommands(self):
        """Check that all the log commands work."""
        root = getLogger()

        with self.assertLogs(level=root.TRACE) as cm:
            root.trace("Trace")
            root.debug("Debug")
            root.verbose("Verbose")
            root.verbose("Verbose with stacklevel", stacklevel=1)
            root.info("Info")
            root.warning("Warning")
            root.fatal("Fatal")
            root.critical("Critical")
            root.error("Error")

        self.assertEqual(len(cm.records), 9)

        # Check that each record has an explicit level name rather than
        # "Level N" and comes from this file (and not the logging.py).
        for record in cm.records:
            self.assertRegex(record.levelname, "^[A-Z]+$")
            self.assertEqual(record.filename, "test_logging.py")

        with self.assertLogs(level=root.DEBUG) as cm:
            # Should only issue the INFO message.
            with root.temporary_log_level(root.INFO):
                root.info("Info")
                root.debug("Debug")
        self.assertEqual(len(cm.records), 1)

        child = root.getChild("child")
        self.assertEqual(child.getEffectiveLevel(), root.getEffectiveLevel())

        # The root logger could be modified by the test environment.
        # We need to pick a level that is different.
        child.setLevel(root.getEffectiveLevel() - 5)
        self.assertNotEqual(child.getEffectiveLevel(), root.getEffectiveLevel())

    def testTraceSetAt(self):
        log_name = "lsst.afw"
        root_level = logging.getLogger().getEffectiveLevel()
        trace_set_at(log_name, 2)
        trace2_log = getLogger(f"TRACE2.{log_name}")
        trace3_log = getLogger(f"TRACE3.{log_name}")
        self.assertEqual(trace2_log.getEffectiveLevel(), logging.DEBUG)
        self.assertEqual(trace3_log.getEffectiveLevel(), logging.INFO)

        # Check that child loggers are affected.
        log_name = "lsst.daf"
        child3_log = getLogger("TRACE3.lsst.daf")
        child2_log = getLogger("TRACE2.lsst.daf")
        self.assertEqual(child3_log.getEffectiveLevel(), root_level)
        self.assertEqual(child2_log.getEffectiveLevel(), root_level)
        trace_set_at("lsst", 2)
        self.assertEqual(child3_log.getEffectiveLevel(), logging.INFO)
        self.assertEqual(child2_log.getEffectiveLevel(), logging.DEBUG)

        # Also check the root logger.
        trace_set_at("", 3)
        self.assertEqual(trace3_log.getEffectiveLevel(), logging.INFO)
        self.assertEqual(getLogger("TRACE3.test").getEffectiveLevel(), logging.DEBUG)

    def test_periodic(self):
        logger = getLogger("test.periodicity")
        periodic = PeriodicLogger(logger)

        # First message will not be issued.
        periodic.log("Message")
        self.assertEqual(periodic.num_issued, 0)

        # Create a new periodic logger with no delay.
        # Every message should be issued.
        periodic = PeriodicLogger(logger, interval=0.0)
        with self.assertLogs(logger.name, level=logger.INFO) as cm:
            periodic.log("Message")
            periodic.log("Message %d", 1)
        self.assertEqual(len(cm.output), 2)
        self.assertEqual(periodic.num_issued, 2)
        self.assertEqual(cm.output[0], f"INFO:{logger.name}:Message")
        self.assertEqual(cm.output[1], f"INFO:{logger.name}:Message 1")
        self.assertEqual(cm.records[0].filename, "test_logging.py", str(cm.records[0]))

        # Create a new periodic logger with small delay.
        # One message should be issued.
        periodic = PeriodicLogger(logger, interval=0.2, level=logger.INFO)
        with self.assertLogs(logger.name, level=logger.INFO) as cm:
            periodic.log("Message")
            time.sleep(0.5)
            issued = periodic.log("Message %d", 1)
            self.assertTrue(issued)
            issued = periodic.log("Message %d", 2)
            self.assertFalse(issued)
        self.assertEqual(periodic.num_issued, 1)
        self.assertEqual(cm.output[0], f"INFO:{logger.name}:Message 1")

        # Again with a standard python Logger.
        pylog = logging.getLogger("python.logger")
        periodic = PeriodicLogger(pylog, interval=0.0, level=logging.DEBUG)
        with self.assertLogs(pylog.name, level=logging.DEBUG) as cm:
            periodic.log("Message")
        self.assertEqual(cm.records[0].filename, "test_logging.py", str(cm.records[0]))

    def test_logstate(self):
        class Myclass:
            x: int = 0
            y: float = 0.0
            z: float = 0.0

            @classmethod
            def method1(cls, x: int) -> None:
                cls.x = x

            @classmethod
            def method2(cls, y: float) -> None:
                cls.y = y

        # set the initial state
        LogState.record((Myclass.method1, 451))
        LogState.record((Myclass.method2, 3.14))

        # check to see how it was set
        state = LogState.get_state()
        first = state[0]
        self.assertEqual(first[0].__func__, Myclass.method1.__func__)
        self.assertEqual(first[1], 451)
        second = state[1]
        self.assertEqual(second[0].__func__, Myclass.method2.__func__)
        self.assertEqual(second[1], 3.14)

        # ask state to be cleared
        LogState.clear_state()

        # make sure it was cleared
        clear_state = LogState.get_state()
        self.assertEqual(len(clear_state), 0)

        # replay the state
        LogState.replay_state(state)

        # check to be sure the state was set as requested
        self.assertEqual(Myclass.x, 451)
        self.assertEqual(Myclass.y, 3.14)

        # try to do it again, and receive a log warning
        LogState.replay_state(state)

        # clear the state; be sure it's cleared
        LogState.clear_state()
        clear_state = LogState.get_state()
        self.assertEqual(len(clear_state), 0)

        # call set state
        LogState.set_state(state)

        # and make sure it was set as requested
        state = LogState.get_state()
        first = state[0]
        self.assertEqual(first[0].__func__, Myclass.method1.__func__)
        self.assertEqual(first[1], 451)
        second = state[1]
        self.assertEqual(second[0].__func__, Myclass.method2.__func__)
        self.assertEqual(second[1], 3.14)


if __name__ == "__main__":
    unittest.main()
