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
classes used to protect method from simultaneous access by different
threads.  The primary class is LockProtected.  
"""
import threading

SharedLock = threading.RLock

class LockProtected(object):
    """
    a class that assists in keeping methods thread-safe.

    This class is intended to be enlisted as a base class to the class being
    protected.  A method that is to be protected from simultaneous access 
    would include (at its beginning) a call to _checkLocked():

    @verbatim
    class MyClass(BaseClass, LockProtected):
        def __init__(self, lock=SharedLock):
            LockProtected.__init__(self, lock)
            ...

        def dangerous(self):
            self._checkLocked()
            ...
    @endverbatim

    Doing so will require that the protected class be "locked" before a 
    protected method can be called or else an UnsafeAccessError will be
    raised.  Locking is done via the with statement:
    @verbatim
    mc = MyClass()
    with mc:
        mc.dangerous()
    @endverbatim

    For the locking to work, the protected class must provide to the
    LockProtected constructor a lock object.  Typically this is a
    lsst.utils.multithreading.SharedLock instance or, if one wants to
    employ thread notification techniques, a
    lsst.utils.multithreading.SharedData instance.  It should at least
    be a reentrant lock--that is, having the behavior of threading.RLock
    (from the standard Python Library).

    This class is primarily intended for protecting methods across multiple
    classes together via a single lock.  That is, it can prevent simultaneous
    access to any protected method across multiple class instances.  To
    accomplish this, each class to be protected should accept a lock as
    a constructor argument.  Then the same lock is passed into all of the
    constructors that need protection together. 
    """

    def __init__(self, lock=None):
        """
        initialize the lock protection
        @param lock   a reentrant lock instance to use.  If None, the
                        protection behavior is disabled.
        """
        # the shared lock
        self._lp_lock = lock

    def __enter__(self):
        if self._lp_lock:
            self._lp_lock.acquire()

    def __exit__(self, exc_type, exc_value, traceback):
        if self._lp_lock:
            self._lp_lock.release()
        return False

    def _checkLocked(self):
        if self._lp_lock and not self._lp_lock._is_owned():
            raise UnsafeAccessError()

class UnsafeAccessError(Exception):
    """
    an exception that is raised when one attempts to access a protected
    method without first acquiring the lock on its class.
    """
    def __init__(self, msg=None):
        if not msg:
            msg = "Programmer Error: failed to obtain lock via with statement"
        Exception.__init__(self, msg)

