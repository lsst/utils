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

#
from __future__ import with_statement
import threading

class SharedData(object):
    """
    @brief a lock-protected container for data that can be shared amongst
    threads.

    This container holds data that is intended to be shared amongst multiple
    threads.  In order to update or (optionally) examine the data, one must
    first aquire the lock associated with the container.

    This container also behaves like a threading.Container, via its 
    wait(), notify(), and notifyAll() functions.  Also like Condition, 
    acquire() is reentrant.  

    SharedData instances may be used with the with statement:
    @verbatim
      sd = SharedData()
      with sd:
          sd.blah = 1
    @endverbatim
    The with statement will acquire the lock and ensure that it is released
    when its block is exited.  
    """

    def __init__(self, needLockOnRead=True, data=None, cond=None):
        """
        create and initialize the shared data
        @param needLockOnRead   if true (default), acquiring the lock will 
                      be needed when reading the data.  This is recommended
                      if the data items are anything but primitive types;
                      otherwise, a compound data item (e.g. of type dict)
                      could be updated without acquiring a lock.  
        @param data   a dictionary of data to initialize the container with.
                      This is done by calling initData().  Set this value to
                      False when calling from a subclass constructor; this
                      will allow any non-protected attributes to be set via
                      the subclass's constructor.  If None is given (default),
                      it is assumed that all new attributes will be considered
                      protected data.
        @param cond   Reuse this existing Condition instance to protect this
                        container
        """
        self._d = {}
        if cond is None:
            cond = threading.Condition()
        self._cond = cond

        # behave like a Condition
        self.acquire   = cond.acquire
        self.release   = cond.release
        self.notify    = cond.notify
        self.notifyAll = cond.notifyAll
        self.wait      = cond.wait
        self.__enter__ = cond.__enter__
        self.__exit__  = cond.__exit__
        self._is_owned = cond._is_owned

        self._lockOnRead = needLockOnRead

        if isinstance(data, dict):
            self.initData(data)
        if data is None:
            self._d["__"] = True

    
    def __getattribute__(self, name):
        if name == "_d" or len(self._d) == 0 or not self._d.has_key(name):
            return object.__getattribute__(self, name)
        
        if self._lockOnRead and not self._is_owned():
            raise AttributeError("%s: lock required for read access" % name)
        return self._d[name]
        

    def __setattr__(self, name, value):
        if name == "_d" or len(self._d) == 0 or name in self.__dict__.keys():
            object.__setattr__(self, name, value)
            return 
        
        if not self._is_owned():
            raise AttributeError("%s: lock required for write access" % name)
        
        self._d[name] = value
        

    def initData(self, data):
        """
        initialize the container with the data from a dictionary.  
        @param data   a dictionary of data to initialize the container with.
                      Attributes will be added to this container with names
                      matching the given the dictionary's key names and
                      initialized to their corresponding values.  The keys
                      cannot match an existing function (or internal attribute)
                      name.
        @throws ValueError   if the dictionary has a key that conflicts with
                      an existing function or internal attribute name.  
        """
        with self._cond:
            bad = []
            realattrs = self.__dict__.keys()
            for key in data.keys():
                if key in realattrs:
                    bad.append(key)
            if len(bad) > 0:
                raise ValueError("Names cause conflicts with functions or " +
                                 "internal data: " + str(bad))

            for key in data.keys():
                self._d[key] = data[key]

            if len(self._d) == 0:
                self._d["__"] = True 

    def dir(self):
        return filter(lambda k: k != "__", self._d.keys())
    
