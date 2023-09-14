# This file is part of utils.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (http://www.lsst.org).
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import inspect
import unittest

from lsst.utils import inheritDoc


class Base:
    """Base class containing some docstrings."""

    def method1() -> None:
        """Return Method 1.

        A note.
        """
        pass

    def method2() -> None:
        """Return Method 2."""
        pass

    def method3() -> None:
        pass

    def method4() -> None:
        """Return Method 4."""
        pass

    def method5() -> None:
        pass

    def method6() -> None:
        """Return Method 6.

        Content."""  # noqa: D209
        pass


class NoInheritDoc(Base):
    """Class that inherits from base class and inherits docstring."""

    def method2() -> None:
        # Docstring inherited.
        pass


class InheritDoc:
    """Class that uses inheritDoc and no explicit inheritance."""

    @inheritDoc(Base)
    def method1() -> None:
        """Note on method 1.

        New line.
        """
        pass

    @inheritDoc(Base)
    def method2() -> None:
        """Note on method 2."""

    @inheritDoc(Base)
    def method3() -> None:
        """Note on method 3."""

    @inheritDoc(Base)
    def method4() -> None:
        # Will inherit even though not parent class.
        pass

    @inheritDoc(Base)
    def method5() -> None:
        # No doc string here or in Base.
        pass

    @inheritDoc(Base)
    def method6() -> None:
        """
        Notes
        -----
        A note.
        """  # noqa: D401
        pass


class InheritDocTestCase(unittest.TestCase):
    """Test inheritDoc functionality."""

    def test_no_inheritdoc(self):
        self.assertIsNone(NoInheritDoc.method2.__doc__)
        self.assertEqual(inspect.getdoc(NoInheritDoc.method2), "Return Method 2.")
        self.assertIsNone(inspect.getdoc(NoInheritDoc.method5))

    def test_inheritDoc(self):
        self.assertEqual(
            inspect.getdoc(InheritDoc.method1),
            """Return Method 1.

A note.

Note on method 1.

New line.""",
        )
        self.assertEqual(
            inspect.getdoc(InheritDoc.method2),
            """Return Method 2.

Note on method 2.""",
        )
        self.assertEqual(inspect.getdoc(InheritDoc.method3), "Note on method 3.")
        self.assertEqual(inspect.getdoc(InheritDoc.method4), "Return Method 4.")
        self.assertIsNone(inspect.getdoc(InheritDoc.method5))

        self.assertEqual(
            inspect.getdoc(InheritDoc.method6),
            """Return Method 6.

Content.

Notes
-----
A note.""",
        )


if __name__ == "__main__":
    unittest.main()
