import unittest
import lsst.utils.tests


class TestCaseOrdering(lsst.utils.tests.TestCase):
    def testTestOrdering(self):
        class DummyTest(lsst.utils.tests.TestCase):
            def noOp(self):
                pass

        class DummyMemoryTest(lsst.utils.tests.MemoryTestCase):
            pass

        suite = unittest.defaultTestLoader.suiteClass([DummyMemoryTest("testLeaks"),
                                                       DummyTest("noOp")])

        self.assertNotIsInstance(suite._tests[0], lsst.utils.tests.MemoryTestCase)
        self.assertIsInstance(suite._tests[-1], lsst.utils.tests.MemoryTestCase)

if __name__ == "__main__":
    unittest.main()
