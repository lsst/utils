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

import unittest

import numpy as np

import lsst.utils
import lsst.utils.tests


class MockClass:  # continued class needs to be at module scope
    """A test class that can be continued."""

    def method1(self):
        return self

    @classmethod
    def method2(cls):
        return cls

    @staticmethod
    def method3():
        return True

    @property
    def property1(self):
        return False


class DecoratorsTestCase(lsst.utils.tests.TestCase):
    """Test the decorators."""

    def setUp(self):
        @lsst.utils.continueClass
        class MockClass:
            def method1a(self):
                return self

            @classmethod
            def method2a(cls):
                return cls

            @staticmethod
            def method3a():
                return True

            @property
            def property1a(self):
                return False

        @lsst.utils.inClass(MockClass)
        def method1b(self):
            return self

        @lsst.utils.inClass(MockClass)
        @classmethod
        def method2b(cls):
            return cls

        @lsst.utils.inClass(MockClass)
        @staticmethod
        def method3b():
            return True

        @lsst.utils.inClass(MockClass)
        @property
        def property1b(self):
            return False

    def testAttributeCopying(self):
        x = MockClass()
        self.assertIs(x.method1(), x)
        self.assertIs(x.method1a(), x)
        self.assertIs(x.method1b(), x)
        self.assertIs(x.method2(), MockClass)
        self.assertIs(x.method2a(), MockClass)
        self.assertIs(x.method2b(), MockClass)
        self.assertIs(MockClass.method2(), MockClass)
        self.assertIs(MockClass.method2a(), MockClass)
        self.assertIs(MockClass.method2b(), MockClass)
        self.assertTrue(x.method3())
        self.assertTrue(x.method3a())
        self.assertTrue(x.method3b())
        self.assertTrue(MockClass.method3())
        self.assertTrue(MockClass.method3a())
        self.assertTrue(MockClass.method3b())
        self.assertFalse(x.property1)
        self.assertFalse(x.property1a)
        self.assertFalse(x.property1b)


class TemplateMetaSimpleTestCase(lsst.utils.tests.TestCase):
    """Test TemplateMeta on a mockup of a template with a single dtype
    template parameter.
    """

    def setUp(self):
        class Example(metaclass=lsst.utils.TemplateMeta):
            def method1(self):
                return self

            @classmethod
            def method2(cls):
                return cls

            @staticmethod
            def method3():
                return True

            @property
            def property1(self):
                return False

        class ExampleF:
            pass

        class ExampleD:
            pass

        self.Example = Example
        self.ExampleF = ExampleF
        self.ExampleD = ExampleD

    def register(self):
        self.Example.register(np.float32, self.ExampleF)
        self.Example.register(np.float64, self.ExampleD)

    def alias(self):
        self.Example.alias("F", self.ExampleF)
        self.Example.alias("D", self.ExampleD)

    def testCorrectRegistration(self):
        self.register()
        self.assertEqual(self.ExampleF.dtype, np.float32)
        self.assertEqual(self.ExampleD.dtype, np.float64)
        self.assertIn(np.float32, self.Example)
        self.assertIn(np.float64, self.Example)
        self.assertEqual(self.Example[np.float32], self.ExampleF)
        self.assertEqual(self.Example[np.float64], self.ExampleD)

    def testAliases(self):
        self.register()
        self.alias()
        self.assertEqual(self.ExampleF.dtype, np.float32)
        self.assertEqual(self.ExampleD.dtype, np.float64)
        self.assertIn("F", self.Example)
        self.assertIn("D", self.Example)
        self.assertEqual(self.Example["F"], self.ExampleF)
        self.assertEqual(self.Example["D"], self.ExampleD)
        self.assertEqual(self.Example["F"], self.Example[np.float32])
        self.assertEqual(self.Example["D"], self.Example[np.float64])

    def testInheritanceHooks(self):
        self.register()
        self.assertTrue(issubclass(self.ExampleF, self.Example))
        self.assertTrue(issubclass(self.ExampleD, self.Example))
        f = self.ExampleF()
        d = self.ExampleD()
        self.assertIsInstance(f, self.Example)
        self.assertIsInstance(d, self.Example)
        self.assertEqual(set(self.Example.__subclasses__()), {self.ExampleF, self.ExampleD})

        # To test fallback code path, ensure that there are multiple
        # examples to check.
        class ExampleSub(self.ExampleD):
            # A subclass that is not itself registered.
            pass

        class Example2(metaclass=lsst.utils.TemplateMeta):
            # A new independent class.
            pass

        class Example2I:
            # Something that will be registered in independent hierarchy.
            pass

        Example2.register(np.int32, Example2I)

        sub = ExampleSub()
        self.assertIsInstance(sub, self.Example)
        self.assertNotIsInstance(sub, Example2)
        self.assertTrue(issubclass(ExampleSub, self.Example))
        self.assertFalse(issubclass(ExampleSub, Example2))

    def testConstruction(self):
        self.register()
        f1 = self.Example(dtype=np.float32)
        # Test that numpy dtype objects resolve to their underlying type
        f2 = self.Example(dtype=np.dtype(np.float32))
        for f in (f1, f2):
            self.assertIsInstance(f, self.Example)
            self.assertIsInstance(f, self.ExampleF)
            self.assertNotIsInstance(f, self.ExampleD)

        with self.assertRaises(TypeError):
            self.Example()
        with self.assertRaises(TypeError):
            self.Example(dtype=np.int32)

    def testAttributeCopying(self):
        self.register()
        f = self.ExampleF()
        d = self.ExampleD()
        self.assertIs(f.method1(), f)
        self.assertIs(d.method1(), d)
        self.assertIs(f.method2(), self.ExampleF)
        self.assertIs(d.method2(), self.ExampleD)
        self.assertIs(self.ExampleF.method2(), self.ExampleF)
        self.assertIs(self.ExampleD.method2(), self.ExampleD)
        self.assertTrue(f.method3())
        self.assertTrue(d.method3())
        self.assertTrue(self.ExampleF.method3())
        self.assertTrue(self.ExampleD.method3())
        self.assertFalse(f.property1)
        self.assertFalse(d.property1)

    def testDictBehavior(self):
        self.register()
        self.assertIn(np.float32, self.Example)
        self.assertEqual(self.Example[np.float32], self.ExampleF)
        self.assertEqual(set(self.Example.keys()), {np.float32, np.float64})
        self.assertEqual(set(self.Example.values()), {self.ExampleF, self.ExampleD})
        self.assertEqual(
            set(self.Example.items()), {(np.float32, self.ExampleF), (np.float64, self.ExampleD)}
        )
        self.assertEqual(len(self.Example), 2)
        self.assertEqual(set(iter(self.Example)), {np.float32, np.float64})
        self.assertEqual(self.Example.get(np.float64), self.ExampleD)
        self.assertEqual(self.Example.get(np.int32, False), False)

    def testNoInheritedDictBehavior(self):
        self.register()
        f = self.ExampleF()
        with self.assertRaises(TypeError):
            len(f)
        with self.assertRaises(TypeError):
            f["F"]
        with self.assertRaises(TypeError):
            for _ in f:
                pass
        with self.assertRaises(TypeError):
            len(self.ExampleF)
        with self.assertRaises(TypeError):
            self.ExampleF["F"]
        with self.assertRaises(TypeError):
            for _ in self.ExampleF:
                pass

    def testAliasUnregistered(self):
        with self.assertRaises(ValueError):
            self.Example.alias("F", self.ExampleF)
        self.assertEqual(len(self.Example), 0)
        self.assertEqual(len(self.Example), 0)

    def testRegisterDTypeTwice(self):
        with self.assertRaises(KeyError):
            self.Example.register("F", self.ExampleF)
            self.Example.register("F", self.ExampleD)
        self.assertEqual(len(self.Example), 1)

    def testRegisterTemplateTwice(self):
        with self.assertRaises(ValueError):
            self.Example.register("F", self.ExampleF)
            self.Example.register("D", self.ExampleF)
        self.assertEqual(len(self.Example), 1)


class TemplateMetaHardTestCase(lsst.utils.tests.TestCase):
    """Test TemplateMeta with a mockup of a template with multiple
    template parameters.
    """

    def setUp(self):
        class Example(metaclass=lsst.utils.TemplateMeta):
            TEMPLATE_PARAMS = ("d", "u")
            TEMPLATE_DEFAULTS = (2, None)

        class Example2F:
            pass

        class Example2D:
            pass

        class Example3F:
            pass

        class Example3D:
            pass

        self.Example = Example
        self.Example2F = Example2F
        self.Example2D = Example2D
        self.Example3F = Example3F
        self.Example3D = Example3D

    def register(self):
        self.Example.register((2, np.float32), self.Example2F)
        self.Example.register((2, np.float64), self.Example2D)
        self.Example.register((3, np.float32), self.Example3F)
        self.Example.register((3, np.float64), self.Example3D)

    def alias(self):
        self.Example.alias("2F", self.Example2F)
        self.Example.alias("2D", self.Example2D)
        self.Example.alias("3F", self.Example3F)
        self.Example.alias("3D", self.Example3D)

    def testCorrectRegistration(self):
        self.register()
        self.assertEqual(self.Example2F.d, 2)
        self.assertEqual(self.Example2F.u, np.float32)
        self.assertEqual(self.Example2D.d, 2)
        self.assertEqual(self.Example2D.u, np.float64)
        self.assertEqual(self.Example3F.d, 3)
        self.assertEqual(self.Example3F.u, np.float32)
        self.assertEqual(self.Example3D.d, 3)
        self.assertEqual(self.Example3D.u, np.float64)
        self.assertIn((2, np.float32), self.Example)
        self.assertIn((2, np.float64), self.Example)
        self.assertIn((3, np.float32), self.Example)
        self.assertIn((3, np.float64), self.Example)
        self.assertEqual(self.Example[2, np.float32], self.Example2F)
        self.assertEqual(self.Example[2, np.float64], self.Example2D)
        self.assertEqual(self.Example[3, np.float32], self.Example3F)
        self.assertEqual(self.Example[3, np.float64], self.Example3D)

    def testAliases(self):
        self.register()
        self.alias()
        self.assertEqual(self.Example2F.d, 2)
        self.assertEqual(self.Example2F.u, np.float32)
        self.assertEqual(self.Example2D.d, 2)
        self.assertEqual(self.Example2D.u, np.float64)
        self.assertEqual(self.Example3F.d, 3)
        self.assertEqual(self.Example3F.u, np.float32)
        self.assertEqual(self.Example3D.d, 3)
        self.assertEqual(self.Example3D.u, np.float64)
        self.assertIn("2F", self.Example)
        self.assertIn("2D", self.Example)
        self.assertIn("3F", self.Example)
        self.assertIn("3D", self.Example)
        self.assertEqual(self.Example["2F"], self.Example2F)
        self.assertEqual(self.Example["2D"], self.Example2D)
        self.assertEqual(self.Example["3F"], self.Example3F)
        self.assertEqual(self.Example["3D"], self.Example3D)

    def testInheritanceHooks(self):
        self.register()
        self.assertTrue(issubclass(self.Example2F, self.Example))
        self.assertTrue(issubclass(self.Example3D, self.Example))
        f = self.Example2F()
        d = self.Example3D()
        self.assertIsInstance(f, self.Example)
        self.assertIsInstance(d, self.Example)
        self.assertEqual(
            set(self.Example.__subclasses__()),
            {self.Example2F, self.Example2D, self.Example3F, self.Example3D},
        )

    def testConstruction(self):
        self.register()
        f = self.Example(u=np.float32)
        self.assertIsInstance(f, self.Example)
        self.assertIsInstance(f, self.Example2F)
        with self.assertRaises(TypeError):
            self.Example()
        with self.assertRaises(TypeError):
            self.Example(u=np.int32, d=1)

    def testDictBehavior(self):
        self.register()
        self.assertIn((2, np.float32), self.Example)
        self.assertEqual(self.Example[2, np.float32], self.Example2F)
        self.assertEqual(
            set(self.Example.keys()),
            {(2, np.float32), (2, np.float64), (3, np.float32), (3, np.float64)},
        )
        self.assertEqual(
            set(self.Example.values()), {self.Example2F, self.Example2D, self.Example3F, self.Example3D}
        )
        self.assertEqual(
            set(self.Example.items()),
            {
                ((2, np.float32), self.Example2F),
                ((2, np.float64), self.Example2D),
                ((3, np.float32), self.Example3F),
                ((3, np.float64), self.Example3D),
            },
        )
        self.assertEqual(len(self.Example), 4)
        self.assertEqual(
            set(iter(self.Example)), {(2, np.float32), (2, np.float64), (3, np.float32), (3, np.float64)}
        )
        self.assertEqual(self.Example.get((3, np.float64)), self.Example3D)
        self.assertEqual(self.Example.get((2, np.int32), False), False)

    def testRegisterBadKey(self):
        with self.assertRaises(ValueError):
            self.Example.register("F", self.Example2F)

    def testRegisterDTypeTwice(self):
        with self.assertRaises(KeyError):
            self.Example.register((2, "F"), self.Example2F)
            self.Example.register((2, "F"), self.Example2D)
        self.assertEqual(len(self.Example), 1)

    def testRegisterTemplateTwice(self):
        with self.assertRaises(ValueError):
            self.Example.register((2, "F"), self.Example2F)
            self.Example.register((2, "D"), self.Example2F)
        self.assertEqual(len(self.Example), 1)


class TestDefaultMethodCopying(lsst.utils.tests.TestCase):
    """Test to determine if static and class methods from a class which is
    registered as a default type in a type ABC are properly copied.
    """

    def setUp(self):
        class Example(metaclass=lsst.utils.TemplateMeta):
            TEMPLATE_PARAMS = ("dtype",)
            TEMPLATE_DEFAULTS = (np.float32,)

        class ExampleF:
            @staticmethod
            def staticCall():
                return 6

            @classmethod
            def classCall(cls):
                return cls

            def regularCall(self):
                return self

        class ExampleI:
            @staticmethod
            def notTransferedStaticCall():
                return 8

            @classmethod
            def notTransferedClassCall(cls):
                return cls

        # Add in a built in function to ExampleF to mimic how pybind11 treats
        # static methods from c++.
        ExampleF.pow = pow

        Example.register(np.float32, ExampleF)
        Example.register(np.int32, ExampleI)
        self.Example = Example
        self.ExampleF = ExampleF
        self.ExampleI = ExampleI

    def testMethodCopyForDefaultType(self):
        # Check that the methods for the default type were transfered and that
        # the regular method was not
        self.assertTrue(hasattr(self.Example, "staticCall"))
        self.assertTrue(hasattr(self.Example, "pow"))
        self.assertTrue(hasattr(self.Example, "classCall"))
        self.assertFalse(hasattr(self.Example, "regularCall"))

        # Verify the default static and class method defaults return the
        # correct values
        self.assertEqual(self.Example.staticCall(), 6)
        self.assertEqual(self.Example.pow(2, 2), 4)
        self.assertIs(self.Example.classCall(), self.ExampleF)

        # Verify static and class methods for non default keys are not
        # transfered
        self.assertFalse(hasattr(self.Example, "notTransferedStaticCall"))
        self.assertFalse(hasattr(self.Example, "notTransferedClassCall"))


if __name__ == "__main__":
    unittest.main()
