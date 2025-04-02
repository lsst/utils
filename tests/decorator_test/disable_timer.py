"""Methods used to test that the appropriate envvar disables the timing
decorator.
"""

import logging
import time

from lsst.utils.timer import timeMethod

log = logging.getLogger("disable_timer")


@timeMethod(logger=log, logLevel=logging.INFO)
def sleep_and_log(self, duration: float) -> None:
    """Check that this does not log if the decorator was disabled on import."""
    time.sleep(duration)


@timeMethod
def sleep_and_nothing(self, duration: float) -> None:
    """Check that this does not have a `__wrapped__` attribute to confirm that
    the decorator is disabled.
    """
    time.sleep(duration)
