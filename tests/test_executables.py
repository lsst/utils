import unittest
import os
import lsst.utils.tests


class ExplicitBinaryTester(lsst.utils.tests.ExecutablesTestCase):

    def testSimpleExe(self):
        """Test explicit shell script"""
        self.assertExecutable("testexe.sh",
                              root_dir=os.path.dirname(__file__),
                              args=["-h"],
                              msg="testexe.sh failed")

        # Try a non-existent test
        with self.assertRaises(Exception):
            self.assertExecutable("testexe-missing.sh")

        # Force test to fail, explicit fail message
        with self.assertRaises(Exception):
            self.assertExecutable("testexe.sh",
                                  root_dir=os.path.dirname(__file__),
                                  args=["-f"],
                                  msg="testexe.sh failed")

        # Force script to fail, default fail message
        with self.assertRaises(Exception):
            self.assertExecutable("testexe.sh",
                                  root_dir=os.path.dirname(__file__),
                                  args=["-f"])


class UtilsBinaryTester(lsst.utils.tests.ExecutablesTestCase):
    pass


EXECUTABLES = None
UtilsBinaryTester.create_executable_tests(__file__, EXECUTABLES)

if __name__ == "__main__":
    unittest.main()
