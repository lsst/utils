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

import sys
import unittest
from collections import Counter

# Classes and functions to use in tests.
import lsst.utils
from lsst.utils import doImport
from lsst.utils._packaging import getPackageDir
from lsst.utils.introspection import (
    find_outside_stacklevel,
    get_caller_name,
    get_class_of,
    get_full_type_name,
    get_instance_of,
    take_object_census,
    trace_object_references,
)


class GetCallerNameTestCase(unittest.TestCase):
    """Test get_caller_name.

    Warning: due to the different ways this can be run
    (e.g. directly or py.test), the module name can be one of two different
    things.
    """

    def test_free_function(self):
        def test_func():
            return get_caller_name(1)

        result = test_func()
        self.assertEqual(result, f"{__name__}.test_func")

    def test_instance_method(self):
        class TestClass:
            def run(self):
                return get_caller_name(1)

        tc = TestClass()
        result = tc.run()
        self.assertEqual(result, f"{__name__}.TestClass.run")

    def test_class_method(self):
        class TestClass:
            @classmethod
            def run(cls):
                return get_caller_name(1)

        tc = TestClass()
        result = tc.run()
        self.assertEqual(result, f"{__name__}.TestClass.run")

    def test_skip(self):
        def test_func(stacklevel):
            return get_caller_name(stacklevel)

        result = test_func(2)
        self.assertEqual(result, f"{__name__}.GetCallerNameTestCase.test_skip")

        result = test_func(2000000)  # use a large number to avoid details of how the test is run
        self.assertEqual(result, "")


class TestInstropection(unittest.TestCase):
    """Tests for lsst.utils.introspection."""

    def testTypeNames(self):
        # Check types and also an object
        tests = [
            (getPackageDir, "lsst.utils.getPackageDir"),  # underscore filtered out
            (int, "int"),
            (0, "int"),
            ("", "str"),
            (doImport, "lsst.utils.doImport.doImport"),  # no underscore
            (Counter, "collections.Counter"),
            (Counter(), "collections.Counter"),
            (lsst.utils, "lsst.utils"),
        ]

        for item, typeName in tests:
            self.assertEqual(get_full_type_name(item), typeName)

    def testUnderscores(self):
        # Underscores are filtered out unless they can't be, either
        # because __init__.py did not import it or there is a clash with
        # the non-underscore version.
        for test_name in (
            "import_test.two._four.simple.Simple",
            "import_test.two._four.clash.Simple",
            "import_test.two.clash.Simple",
        ):
            test_cls = get_class_of(test_name)
            self.assertTrue(test_cls.true())
            full = get_full_type_name(test_cls)
            self.assertEqual(full, test_name)

    def testGetClassOf(self):
        tests = [(doImport, "lsst.utils.doImport"), (Counter, "collections.Counter")]

        for test in tests:
            ref_type = test[0]
            for t in test:
                c = get_class_of(t)
                self.assertIs(c, ref_type)

    def testGetInstanceOf(self):
        c = get_instance_of("collections.Counter", "abcdeab")
        self.assertIsInstance(c, Counter)
        self.assertEqual(c["a"], 2)
        with self.assertRaises(TypeError) as cm:
            get_instance_of(lsst.utils)
        self.assertIn("lsst.utils", str(cm.exception))

    def test_stacklevel(self):
        level = find_outside_stacklevel("lsst.utils")
        self.assertEqual(level, 1)

        info = {}
        level = find_outside_stacklevel("lsst.utils", stack_info=info)
        self.assertIn("test_introspection.py", info["filename"])

        c = doImport("import_test.two.three.success.Container")
        with self.assertWarns(Warning) as cm:
            level = c.level()
        self.assertTrue(cm.filename.endswith("test_introspection.py"))
        self.assertEqual(level, 2)
        with self.assertWarns(Warning) as cm:
            level = c.indirect_level()
        self.assertTrue(cm.filename.endswith("test_introspection.py"))
        self.assertEqual(level, 3)

        # Test with additional options.
        with self.assertWarns(Warning) as cm:
            level = c.indirect_level(allow_methods={"indirect_level"})
        self.assertEqual(level, 2)
        self.assertTrue(cm.filename.endswith("success.py"))

        # Adjust test on python 3.10.
        allow_methods = {"import_test.two.three.success.Container.level"}
        stacklevel = 1
        if sys.version_info < (3, 11, 0):
            # python 3.10 does not support "." syntax and will filter it out.
            allow_methods.add("indirect_level")
            stacklevel = 2
        with self.assertWarns(FutureWarning) as cm:
            level = c.indirect_level(allow_methods=allow_methods)
        self.assertEqual(level, stacklevel)
        self.assertTrue(cm.filename.endswith("success.py"))

    def test_take_object_census(self):
        # Full output cannot be validated, because it depends on the global
        # state of the test process.
        class DummyClass:
            pass

        dummy = DummyClass()  # noqa: F841, unused variable

        counts = take_object_census()
        self.assertIsInstance(counts, Counter)
        self.assertEqual(counts[DummyClass], 1)

    def test_trace_object_references_simple(self):
        class RefTester:
            pass

        obj1 = RefTester()
        obj2 = RefTester()
        mapping = {"2": obj2}

        trace, complete = trace_object_references(RefTester)  # max_level = 10
        self.assertTrue(complete)
        self.assertEqual(len(trace), 2)
        # The local namespace is *not* counted as a referring object.
        self.assertEqual(set(trace[0]), {obj1, obj2})
        self.assertEqual(list(trace[1]), [mapping])

    def test_trace_object_references_atlimit(self):
        """Test that completion is detected when trace ends *just* at
        the limit.
        """

        class RefTester:
            pass

        obj1 = RefTester()
        obj2 = RefTester()
        mapping = {"2": obj2}

        trace, complete = trace_object_references(RefTester, max_level=1)
        self.assertTrue(complete)
        self.assertEqual(len(trace), 2)
        # The local namespace is *not* counted as a referring object.
        self.assertEqual(set(trace[0]), {obj1, obj2})
        self.assertEqual(list(trace[1]), [mapping])

    def test_trace_object_references_cyclic(self):
        class RefTester:
            pass

        obj1 = RefTester()
        obj2 = RefTester()
        mapping = {"2": obj2}
        cyclic = {"back": mapping}
        mapping["forth"] = cyclic

        trace, complete = trace_object_references(RefTester, max_level=3)
        self.assertFalse(complete)
        self.assertEqual(len(trace), 4)
        # The local namespace is *not* counted as a referring object.
        self.assertEqual(set(trace[0]), {obj1, obj2})
        self.assertEqual(list(trace[1]), [mapping])
        self.assertEqual(list(trace[2]), [cyclic])
        self.assertEqual(list(trace[3]), [mapping])

    def test_trace_object_references_null(self):
        class UnusedClass:
            pass

        trace, complete = trace_object_references(UnusedClass)
        self.assertTrue(complete)
        self.assertEqual(len(trace), 1)
        self.assertEqual(list(trace[0]), [])


if __name__ == "__main__":
    unittest.main()
