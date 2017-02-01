from __future__ import absolute_import, division, print_function

from future.utils import with_metaclass

import numpy as np
import unittest
import lsst.utils.tests


class MockClass:   # continued class needs to be at module scope

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


class TemplateMetaTestCase(lsst.utils.tests.TestCase):

    def setUp(self):

        class Base(with_metaclass(lsst.utils.TemplateMeta, object)):

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

        class DerivedF:
            pass

        class DerivedD:
            pass

        self.Base = Base
        self.DerivedF = DerivedF
        self.DerivedD = DerivedD

    def register(self):
        self.Base.register(np.float32, self.DerivedF)
        self.Base.register(np.float64, self.DerivedD)

    def alias(self):
        self.Base.alias("F", self.DerivedF)
        self.Base.alias("D", self.DerivedD)

    def testCorrectRegistration(self):
        self.register()
        self.assertEqual(self.DerivedF.dtype, np.float32)
        self.assertEqual(self.DerivedD.dtype, np.float64)
        self.assertIn(np.float32, self.Base)
        self.assertIn(np.float64, self.Base)
        self.assertEqual(self.Base[np.float32], self.DerivedF)
        self.assertEqual(self.Base[np.float64], self.DerivedD)

    def testAliases(self):
        self.register()
        self.alias()
        self.assertEqual(self.DerivedF.dtype, np.float32)
        self.assertEqual(self.DerivedD.dtype, np.float64)
        self.assertIn("F", self.Base)
        self.assertIn("D", self.Base)
        self.assertEqual(self.Base["F"], self.DerivedF)
        self.assertEqual(self.Base["D"], self.DerivedD)

    def testInheritanceHooks(self):
        self.register()
        self.assertTrue(issubclass(self.DerivedF, self.Base))
        self.assertTrue(issubclass(self.DerivedD, self.Base))
        f = self.DerivedF()
        d = self.DerivedD()
        self.assertIsInstance(f, self.Base)
        self.assertIsInstance(d, self.Base)
        self.assertEqual(set(self.Base.__subclasses__()), set([self.DerivedF, self.DerivedD]))

    def testConstruction(self):
        self.register()
        f = self.Base(dtype=np.float32)
        self.assertIsInstance(f, self.Base)
        self.assertIsInstance(f, self.DerivedF)
        with self.assertRaises(TypeError):
            self.Base()
        with self.assertRaises(TypeError):
            self.Base(dtype=np.int32)

    def testAttributeCopying(self):
        self.register()
        f = self.DerivedF()
        d = self.DerivedD()
        self.assertIs(f.method1(), f)
        self.assertIs(d.method1(), d)
        self.assertIs(f.method2(), self.DerivedF)
        self.assertIs(d.method2(), self.DerivedD)
        self.assertIs(self.DerivedF.method2(), self.DerivedF)
        self.assertIs(self.DerivedD.method2(), self.DerivedD)
        self.assertTrue(f.method3())
        self.assertTrue(d.method3())
        self.assertTrue(self.DerivedF.method3())
        self.assertTrue(self.DerivedD.method3())
        self.assertFalse(f.property1)
        self.assertFalse(d.property1)

    def testDictBehavior(self):
        self.register()
        self.assertIn(np.float32, self.Base)
        self.assertEqual(self.Base[np.float32], self.DerivedF)
        self.assertEqual(set(self.Base.keys()), set([np.float32, np.float64]))
        self.assertEqual(set(self.Base.values()), set([self.DerivedF, self.DerivedD]))
        self.assertEqual(set(self.Base.items()), set([(np.float32, self.DerivedF),
                                                      (np.float64, self.DerivedD)]))
        self.assertEqual(len(self.Base), 2)
        self.assertEqual(set(iter(self.Base)), set([np.float32, np.float64]))
        self.assertEqual(self.Base.get(np.float64), self.DerivedD)
        self.assertEqual(self.Base.get(np.int32, False), False)

    def testNoInheritedDictBehavior(self):
        self.register()
        f = self.DerivedF()
        with self.assertRaises(TypeError):
            len(f)
        with self.assertRaises(TypeError):
            f["F"]
        with self.assertRaises(TypeError):
            for x in f:
                pass
        with self.assertRaises(TypeError):
            len(self.DerivedF)
        with self.assertRaises(TypeError):
            self.DerivedF["F"]
        with self.assertRaises(TypeError):
            for x in self.DerivedF:
                pass

    def testAliasUnregistered(self):
        with self.assertRaises(ValueError):
            self.Base.alias("F", self.DerivedF)
        self.assertEqual(len(self.Base), 0)
        with self.assertRaises(ValueError):
            self.DerivedF.dtype = "D"
            self.Base.alias("F", self.DerivedF)
        self.assertEqual(len(self.Base), 0)

    def testRegisterDTypeTwice(self):
        with self.assertRaises(KeyError):
            self.Base.register("F", self.DerivedF)
            self.Base.register("F", self.DerivedD)
        self.assertEqual(len(self.Base), 1)

    def testRegisterTemplateTwice(self):
        with self.assertRaises(ValueError):
            self.Base.register("F", self.DerivedF)
            self.Base.register("D", self.DerivedF)
        self.assertEqual(len(self.Base), 1)


if __name__ == "__main__":
    unittest.main()
