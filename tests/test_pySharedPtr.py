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
#

import gc
import unittest

import lsst.utils.tests
import _inheritance


class PySharedPtrTestSuite(lsst.utils.tests.TestCase):
    """Test the ability of PySharedPtr to safely pass hybrid objects
    between C++ and Python."""

    class PyDerived(_inheritance.CppBase):
        def __init__(self):
            super().__init__()

        # Don't override overridable()

        def abstract(self):
            return "py-abstract"

    class PyCppDerived(_inheritance.CppDerived):
        def __init__(self):
            super().__init__()

        def nonOverridable(self):
            return "error -- should never be called!"

        def overridable(self):
            return "py-override"

        def abstract(self):
            return "py-abstract"

    def checkGarbageCollection(self, concreteClass, returns):
        """Generic test for whether a C++/Python class survives garbage collection.

        Parameters
        ----------
        concreteClass : `_inheritance.CppBase`-type
            The class to test. Must be default-constructible.
        returns : `tuple`
            A tuple of the return values from ``concreteClass``'s
            ``nonOverridable``, ``overridable``, and ``abstract`` methods, in
            that order.
        """
        storage = _inheritance.CppStorage(concreteClass())

        gc.collect()

        retrieved = _inheritance.getFromStorage(storage)
        self.assertIsInstance(retrieved, _inheritance.CppBase)
        self.assertIsInstance(retrieved, concreteClass)
        self.assertEqual(_inheritance.printFromCpp(retrieved), " ".join(returns))

    def testPyDerivedGarbageCollection(self):
        self.checkGarbageCollection(self.PyDerived, ("42", "", "py-abstract"))

    def testCppDerivedGarbageCollection(self):
        self.checkGarbageCollection(_inheritance.CppDerived, ("42", "overridden", "implemented"))

    def testPyCppDerivedGarbageCollection(self):
        self.checkGarbageCollection(self.PyCppDerived, ("42", "py-override", "py-abstract"))


class TestMemory(lsst.utils.tests.MemoryTestCase):
    pass


def setup_module(module):
    lsst.utils.tests.init()


if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()
