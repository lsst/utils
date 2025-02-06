# This file is part of utils.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# Use of this source code is governed by a 3-clause BSD-style
# license that can be found in the LICENSE file.

"""Support code for running unit tests."""

from __future__ import annotations

__all__ = [
    "ExecutablesTestCase",
    "ImportTestCase",
    "MemoryTestCase",
    "TestCase",
    "assertFloatsAlmostEqual",
    "assertFloatsEqual",
    "assertFloatsNotEqual",
    "classParameters",
    "debugger",
    "getTempFilePath",
    "init",
    "methodParameters",
    "temporaryDirectory",
]

import contextlib
import functools
import gc
import inspect
import itertools
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import warnings
from collections.abc import Callable, Container, Iterable, Iterator, Mapping, Sequence
from importlib import resources
from typing import Any, ClassVar

import numpy
import psutil

from .doImport import doImport

# Initialize the list of open files to an empty set
open_files = set()


def _get_open_files() -> set[str]:
    """Return a set containing the list of files currently open in this
    process.

    Returns
    -------
    open_files : `set`
        Set containing the list of open files.
    """
    return {p.path for p in psutil.Process().open_files()}


def init() -> None:
    """Initialize the memory tester and file descriptor leak tester."""
    global open_files
    # Reset the list of open files
    open_files = _get_open_files()


def sort_tests(tests) -> unittest.TestSuite:
    """Sort supplied test suites such that MemoryTestCases are at the end.

    `lsst.utils.tests.MemoryTestCase` tests should always run after any other
    tests in the module.

    Parameters
    ----------
    tests : sequence
        Sequence of test suites.

    Returns
    -------
    suite : `unittest.TestSuite`
        A combined `~unittest.TestSuite` with
        `~lsst.utils.tests.MemoryTestCase` at the end.
    """
    suite = unittest.TestSuite()
    memtests = []
    for test_suite in tests:
        try:
            # Just test the first test method in the suite for MemoryTestCase
            # Use loop rather than next as it is possible for a test class
            # to not have any test methods and the Python community prefers
            # for loops over catching a StopIteration exception.
            bases = None
            for method in test_suite:
                bases = inspect.getmro(method.__class__)
                break
            if bases is not None and MemoryTestCase in bases:
                memtests.append(test_suite)
            else:
                suite.addTests(test_suite)
        except TypeError:
            if isinstance(test_suite, MemoryTestCase):
                memtests.append(test_suite)
            else:
                suite.addTest(test_suite)
    suite.addTests(memtests)
    return suite


def _suiteClassWrapper(tests):
    return unittest.TestSuite(sort_tests(tests))


# Replace the suiteClass callable in the defaultTestLoader
# so that we can reorder the test ordering. This will have
# no effect if no memory test cases are found.
unittest.defaultTestLoader.suiteClass = _suiteClassWrapper


class MemoryTestCase(unittest.TestCase):
    """Check for resource leaks."""

    ignore_regexps: ClassVar[list[str]] = []
    """List of regexps to ignore when checking for open files."""

    @classmethod
    def tearDownClass(cls) -> None:
        """Reset the leak counter when the tests have been completed."""
        init()

    def testFileDescriptorLeaks(self) -> None:
        """Check if any file descriptors are open since init() called.

        Ignores files with certain known path components and any files
        that match regexp patterns in class property ``ignore_regexps``.
        """
        gc.collect()
        global open_files
        now_open = _get_open_files()

        # Some files are opened out of the control of the stack.
        now_open = {
            f
            for f in now_open
            if not f.endswith(".car")
            and not f.startswith("/proc/")
            and not f.startswith("/sys/")
            and not f.endswith(".ttf")
            and not (f.startswith("/var/lib/") and f.endswith("/passwd"))
            and not f.endswith("astropy.log")
            and not f.endswith("mime/mime.cache")
            and not f.endswith(".sqlite3")
            and not any(re.search(r, f) for r in self.ignore_regexps)
        }

        diff = now_open.difference(open_files)
        if diff:
            for f in diff:
                print(f"File open: {f}")
            self.fail(f"Failed to close {len(diff)} file{'s' if len(diff) != 1 else ''}")


class ExecutablesTestCase(unittest.TestCase):
    """Test that executables can be run and return good status.

    The test methods are dynamically created. Callers
    must subclass this class in their own test file and invoke
    the create_executable_tests() class method to register the tests.
    """

    TESTS_DISCOVERED = -1

    @classmethod
    def setUpClass(cls) -> None:
        """Abort testing if automated test creation was enabled and
        no tests were found.
        """
        if cls.TESTS_DISCOVERED == 0:
            raise RuntimeError("No executables discovered.")

    def testSanity(self) -> None:
        """Ensure that there is at least one test to be
        executed. This allows the test runner to trigger the class set up
        machinery to test whether there are some executables to test.
        """

    def assertExecutable(
        self,
        executable: str,
        root_dir: str | None = None,
        args: Sequence[str] | None = None,
        msg: str | None = None,
    ) -> None:
        """Check an executable runs and returns good status.

        Prints output to standard out. On bad exit status the test
        fails. If the executable can not be located the test is skipped.

        Parameters
        ----------
        executable : `str`
            Path to an executable. ``root_dir`` is not used if this is an
            absolute path.
        root_dir : `str`, optional
            Directory containing executable. Ignored if `None`.
        args : `list` or `tuple`, optional
            Arguments to be provided to the executable.
        msg : `str`, optional
            Message to use when the test fails. Can be `None` for default
            message.

        Raises
        ------
        AssertionError
            The executable did not return 0 exit status.
        """
        if root_dir is not None and not os.path.isabs(executable):
            executable = os.path.join(root_dir, executable)

        # Form the argument list for subprocess
        sp_args = [executable]
        argstr = "no arguments"
        if args is not None:
            sp_args.extend(args)
            argstr = 'arguments "' + " ".join(args) + '"'

        print(f"Running executable '{executable}' with {argstr}...")
        if not os.path.exists(executable):
            self.skipTest(f"Executable {executable} is unexpectedly missing")
        failmsg = None
        try:
            output = subprocess.check_output(sp_args)
        except subprocess.CalledProcessError as e:
            output = e.output
            failmsg = f"Bad exit status from '{executable}': {e.returncode}"
        print(output.decode("utf-8"))
        if failmsg:
            if msg is None:
                msg = failmsg
            self.fail(msg)

    @classmethod
    def _build_test_method(cls, executable: str, root_dir: str) -> None:
        """Build a test method and attach to class.

        A test method is created for the supplied excutable located
        in the supplied root directory. This method is attached to the class
        so that the test runner will discover the test and run it.

        Parameters
        ----------
        cls : `object`
            The class in which to create the tests.
        executable : `str`
            Name of executable. Can be absolute path.
        root_dir : `str`
            Path to executable. Not used if executable path is absolute.
        """
        if not os.path.isabs(executable):
            executable = os.path.abspath(os.path.join(root_dir, executable))

        # Create the test name from the executable path.
        test_name = "test_exe_" + executable.replace("/", "_")

        # This is the function that will become the test method
        def test_executable_runs(*args: Any) -> None:
            self = args[0]
            self.assertExecutable(executable)

        # Give it a name and attach it to the class
        test_executable_runs.__name__ = test_name
        setattr(cls, test_name, test_executable_runs)

    @classmethod
    def create_executable_tests(cls, ref_file: str, executables: Sequence[str] | None = None) -> None:
        """Discover executables to test and create corresponding test methods.

        Scans the directory containing the supplied reference file
        (usually ``__file__`` supplied from the test class) to look for
        executables. If executables are found a test method is created
        for each one. That test method will run the executable and
        check the returned value.

        Executable scripts with a ``.py`` extension and shared libraries
        are ignored by the scanner.

        This class method must be called before test discovery.

        Parameters
        ----------
        ref_file : `str`
            Path to a file within the directory to be searched.
            If the files are in the same location as the test file, then
            ``__file__`` can be used.
        executables : `list` or `tuple`, optional
            Sequence of executables that can override the automated
            detection. If an executable mentioned here is not found, a
            skipped test will be created for it, rather than a failed
            test.

        Examples
        --------
        >>> cls.create_executable_tests(__file__)
        """
        # Get the search directory from the reference file
        ref_dir = os.path.abspath(os.path.dirname(ref_file))

        if executables is None:
            # Look for executables to test by walking the tree
            executables = []
            for root, _, files in os.walk(ref_dir):
                for f in files:
                    # Skip Python files. Shared libraries are executable.
                    if not f.endswith(".py") and not f.endswith(".so"):
                        full_path = os.path.join(root, f)
                        if os.access(full_path, os.X_OK):
                            executables.append(full_path)

        # Store the number of tests found for later assessment.
        # Do not raise an exception if we have no executables as this would
        # cause the testing to abort before the test runner could properly
        # integrate it into the failure report.
        cls.TESTS_DISCOVERED = len(executables)

        # Create the test functions and attach them to the class
        for e in executables:
            cls._build_test_method(e, ref_dir)


class ImportTestCase(unittest.TestCase):
    """Test that the named packages can be imported and all files within
    that package.

    The test methods are created dynamically. Callers must subclass this
    method and define the ``PACKAGES`` property.
    """

    PACKAGES: ClassVar[Iterable[str]] = ()
    """Packages to be imported."""

    SKIP_FILES: ClassVar[Mapping[str, Container[str]]] = {}
    """Files to be skipped importing; specified as key-value pairs.

    The key is the package name and the value is a set of files names in that
    package to skip.

    Note: Files with names not ending in .py or beginning with leading double
    underscores are always skipped.
    """

    _n_registered = 0
    """Number of packages registered for testing by this class."""

    def _test_no_packages_registered_for_import_testing(self) -> None:
        """Test when no packages have been registered.

        Without this, if no packages have been listed no tests will be
        registered and the test system will not report on anything. This
        test fails and reports why.
        """
        raise AssertionError("No packages registered with import test. Was the PACKAGES property set?")

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Create the test methods based on the content of the ``PACKAGES``
        class property.
        """
        super().__init_subclass__(**kwargs)

        for mod in cls.PACKAGES:
            test_name = "test_import_" + mod.replace(".", "_")

            def test_import(*args: Any, mod=mod) -> None:
                self = args[0]
                self.assertImport(mod)

            test_import.__name__ = test_name
            setattr(cls, test_name, test_import)
            cls._n_registered += 1

        # If there are no packages listed that is likely a mistake and
        # so register a failing test.
        if cls._n_registered == 0:
            cls.test_no_packages_registered = cls._test_no_packages_registered_for_import_testing

    def assertImport(self, root_pkg):
        for file in resources.files(root_pkg).iterdir():
            file = file.name
            # When support for python 3.9 is dropped, this could be updated to
            # use match case construct.
            if not file.endswith(".py"):
                continue
            if file.startswith("__"):
                continue
            if file in self.SKIP_FILES.get(root_pkg, ()):
                continue
            root, _ = os.path.splitext(file)
            module_name = f"{root_pkg}.{root}"
            with self.subTest(module=module_name):
                try:
                    doImport(module_name)
                except ImportError as e:
                    raise AssertionError(f"Error importing module {module_name}: {e}") from e


@contextlib.contextmanager
def getTempFilePath(ext: str, expectOutput: bool = True) -> Iterator[str]:
    """Return a path suitable for a temporary file and try to delete the
    file on success.

    If the with block completes successfully then the file is deleted,
    if possible; failure results in a printed warning.
    If a file is remains when it should not, a RuntimeError exception is
    raised. This exception is also raised if a file is not present on context
    manager exit when one is expected to exist.
    If the block exits with an exception the file if left on disk so it can be
    examined. The file name has a random component such that nested context
    managers can be used with the same file suffix.

    Parameters
    ----------
    ext : `str`
        File name extension, e.g. ``.fits``.
    expectOutput : `bool`, optional
        If `True`, a file should be created within the context manager.
        If `False`, a file should not be present when the context manager
        exits.

    Yields
    ------
    path : `str`
        Path for a temporary file. The path is a combination of the caller's
        file path and the name of the top-level function.

    Examples
    --------
    .. code-block:: python

        # file tests/testFoo.py
        import unittest
        import lsst.utils.tests


        class FooTestCase(unittest.TestCase):
            def testBasics(self):
                self.runTest()

            def runTest(self):
                with lsst.utils.tests.getTempFilePath(".fits") as tmpFile:
                    # if tests/.tests exists then
                    # tmpFile = "tests/.tests/testFoo_testBasics.fits"
                    # otherwise tmpFile = "testFoo_testBasics.fits"
                    ...
                    # at the end of this "with" block the path tmpFile will be
                    # deleted, but only if the file exists and the "with"
                    # block terminated normally (rather than with an exception)


        ...
    """
    stack = inspect.stack()
    # get name of first function in the file
    for i in range(2, len(stack)):
        frameInfo = inspect.getframeinfo(stack[i][0])
        if i == 2:
            callerFilePath = frameInfo.filename
            callerFuncName = frameInfo.function
        elif callerFilePath == frameInfo.filename:
            # this function called the previous function
            callerFuncName = frameInfo.function
        else:
            break

    callerDir, callerFileNameWithExt = os.path.split(callerFilePath)
    callerFileName = os.path.splitext(callerFileNameWithExt)[0]
    outDir = os.path.join(callerDir, ".tests")
    if not os.path.isdir(outDir):
        # No .tests directory implies we are not running with sconsUtils.
        # Need to use the current working directory, the callerDir, or
        # /tmp equivalent. If cwd is used if must be as an absolute path
        # in case the test code changes cwd.
        outDir = os.path.abspath(os.path.curdir)
    prefix = f"{callerFileName}_{callerFuncName}-"
    outPath = tempfile.mktemp(dir=outDir, suffix=ext, prefix=prefix)
    if os.path.exists(outPath):
        # There should not be a file there given the randomizer. Warn and
        # remove.
        # Use stacklevel 3 so that the warning is reported from the end of the
        # with block
        warnings.warn(f"Unexpectedly found pre-existing tempfile named {outPath!r}", stacklevel=3)
        with contextlib.suppress(OSError):
            os.remove(outPath)

    yield outPath

    fileExists = os.path.exists(outPath)
    if expectOutput:
        if not fileExists:
            raise RuntimeError(f"Temp file expected named {outPath} but none found")
    else:
        if fileExists:
            raise RuntimeError(f"Unexpectedly discovered temp file named {outPath}")
    # Try to clean up the file regardless
    if fileExists:
        try:
            os.remove(outPath)
        except OSError as e:
            # Use stacklevel 3 so that the warning is reported from the end of
            # the with block.
            warnings.warn(f"Warning: could not remove file {outPath!r}: {e}", stacklevel=3)


class TestCase(unittest.TestCase):
    """Subclass of unittest.TestCase that adds some custom assertions for
    convenience.
    """


def inTestCase(func: Callable) -> Callable:
    """Add a free function to our custom TestCase class, while
    also making it available as a free function.

    Parameters
    ----------
    func : `~collections.abc.Callable`
        Function to be added to `unittest.TestCase` class.

    Returns
    -------
    func : `~collections.abc.Callable`
        The given function.
    """
    setattr(TestCase, func.__name__, func)
    return func


def debugger(*exceptions):
    """Enter the debugger when there's an uncaught exception.

    To use, just slap a ``@debugger()`` on your function.

    You may provide specific exception classes to catch as arguments to
    the decorator function, e.g.,
    ``@debugger(RuntimeError, NotImplementedError)``.
    This defaults to just `AssertionError`, for use on `unittest.TestCase`
    methods.

    Code provided by "Rosh Oxymoron" on StackOverflow:
    http://stackoverflow.com/questions/4398967/python-unit-testing-automatically-running-the-debugger-when-a-test-fails

    Parameters
    ----------
    *exceptions : `Exception`
        Specific exception classes to catch. Default is to catch
        `AssertionError`.

    Notes
    -----
    Consider using ``pytest --pdb`` instead of this decorator.
    """
    if not exceptions:
        exceptions = (Exception,)

    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except exceptions:
                import pdb
                import sys

                pdb.post_mortem(sys.exc_info()[2])

        return wrapper

    return decorator


def plotImageDiff(
    lhs: numpy.ndarray,
    rhs: numpy.ndarray,
    bad: numpy.ndarray | None = None,
    diff: numpy.ndarray | None = None,
    plotFileName: str | None = None,
) -> None:
    """Plot the comparison of two 2-d NumPy arrays.

    Parameters
    ----------
    lhs : `numpy.ndarray`
        LHS values to compare; a 2-d NumPy array.
    rhs : `numpy.ndarray`
        RHS values to compare; a 2-d NumPy array.
    bad : `numpy.ndarray`
        A 2-d boolean NumPy array of values to emphasize in the plots.
    diff : `numpy.ndarray`
        Difference array; a 2-d NumPy array, or None to show lhs-rhs.
    plotFileName : `str`
        Filename to save the plot to.  If None, the plot will be displayed in
        a window.

    Notes
    -----
    This method uses `matplotlib` and imports it internally; it should be
    wrapped in a try/except block within packages that do not depend on
    `matplotlib` (including `~lsst.utils`).
    """
    if plotFileName is None:
        # We need to create an interactive plot with pyplot.
        from matplotlib import pyplot

        fig = pyplot.figure()
    else:
        # We can create a non-interactive figure.
        from .plotting import make_figure

        fig = make_figure()

    if diff is None:
        diff = lhs - rhs

    if bad is not None:
        # make an rgba image that's red and transparent where not bad
        badImage = numpy.zeros(bad.shape + (4,), dtype=numpy.uint8)
        badImage[:, :, 0] = 255
        badImage[:, :, 1] = 0
        badImage[:, :, 2] = 0
        badImage[:, :, 3] = 255 * bad
    vmin1 = numpy.minimum(numpy.min(lhs), numpy.min(rhs))
    vmax1 = numpy.maximum(numpy.max(lhs), numpy.max(rhs))
    vmin2 = numpy.min(diff)
    vmax2 = numpy.max(diff)
    for n, (image, title) in enumerate([(lhs, "lhs"), (rhs, "rhs"), (diff, "diff")]):
        ax = fig.add_subplot(2, 3, n + 1)
        im1 = ax.imshow(
            image, cmap=pyplot.cm.gray, interpolation="nearest", origin="lower", vmin=vmin1, vmax=vmax1
        )
        if bad is not None:
            ax.imshow(badImage, alpha=0.2, interpolation="nearest", origin="lower")
        ax.axis("off")
        ax.set_title(title)
        ax = fig.add_subplot(2, 3, n + 4)
        im2 = ax.imshow(
            image, cmap=pyplot.cm.gray, interpolation="nearest", origin="lower", vmin=vmin2, vmax=vmax2
        )
        if bad is not None:
            ax.imshow(badImage, alpha=0.2, interpolation="nearest", origin="lower")
        ax.axis("off")
        ax.set_title(title)
    fig.subplots_adjust(left=0.05, bottom=0.05, top=0.92, right=0.75, wspace=0.05, hspace=0.05)
    cax1 = fig.add_subplot([0.8, 0.55, 0.05, 0.4])
    fig.colorbar(im1, cax=cax1)
    cax2 = fig.add_subplot([0.8, 0.05, 0.05, 0.4])
    fig.colorbar(im2, cax=cax2)
    if plotFileName:
        fig.savefig(plotFileName)
    else:
        pyplot.show()


@inTestCase
def assertFloatsAlmostEqual(
    testCase: unittest.TestCase,
    lhs: float | numpy.ndarray,
    rhs: float | numpy.ndarray,
    rtol: float | None = sys.float_info.epsilon,
    atol: float | None = sys.float_info.epsilon,
    relTo: float | None = None,
    printFailures: bool = True,
    plotOnFailure: bool = False,
    plotFileName: str | None = None,
    invert: bool = False,
    msg: str | None = None,
    ignoreNaNs: bool = False,
) -> None:
    """Highly-configurable floating point comparisons for scalars and arrays.

    The test assertion will fail if all elements ``lhs`` and ``rhs`` are not
    equal to within the tolerances specified by ``rtol`` and ``atol``.
    More precisely, the comparison is:

    ``abs(lhs - rhs) <= relTo*rtol OR abs(lhs - rhs) <= atol``

    If ``rtol`` or ``atol`` is `None`, that term in the comparison is not
    performed at all.

    When not specified, ``relTo`` is the elementwise maximum of the absolute
    values of ``lhs`` and ``rhs``.  If set manually, it should usually be set
    to either ``lhs`` or ``rhs``, or a scalar value typical of what is
    expected.

    Parameters
    ----------
    testCase : `unittest.TestCase`
        Instance the test is part of.
    lhs : scalar or array-like
        LHS value(s) to compare; may be a scalar or array-like of any
        dimension.
    rhs : scalar or array-like
        RHS value(s) to compare; may be a scalar or array-like of any
        dimension.
    rtol : `float`, optional
        Relative tolerance for comparison; defaults to double-precision
        epsilon.
    atol : `float`, optional
        Absolute tolerance for comparison; defaults to double-precision
        epsilon.
    relTo : `float`, optional
        Value to which comparison with rtol is relative.
    printFailures : `bool`, optional
        Upon failure, print all inequal elements as part of the message.
    plotOnFailure : `bool`, optional
        Upon failure, plot the originals and their residual with matplotlib.
        Only 2-d arrays are supported.
    plotFileName : `str`, optional
        Filename to save the plot to.  If `None`, the plot will be displayed in
        a window.
    invert : `bool`, optional
        If `True`, invert the comparison and fail only if any elements *are*
        equal. Used to implement `~lsst.utils.tests.assertFloatsNotEqual`,
        which should generally be used instead for clarity.
        will return `True`).
    msg : `str`, optional
        String to append to the error message when assert fails.
    ignoreNaNs : `bool`, optional
        If `True` (`False` is default) mask out any NaNs from operand arrays
        before performing comparisons if they are in the same locations; NaNs
        in different locations are trigger test assertion failures, even when
        ``invert=True``.  Scalar NaNs are treated like arrays containing only
        NaNs of the same shape as the other operand, and no comparisons are
        performed if both sides are scalar NaNs.

    Raises
    ------
    AssertionError
        The values are not almost equal.
    """
    if ignoreNaNs:
        lhsMask = numpy.isnan(lhs)
        rhsMask = numpy.isnan(rhs)
        if not numpy.all(lhsMask == rhsMask):
            testCase.fail(
                f"lhs has {lhsMask.sum()} NaN values and rhs has {rhsMask.sum()} NaN values, "
                "in different locations."
            )
        if numpy.all(lhsMask):
            assert numpy.all(rhsMask), "Should be guaranteed by previous if."
            # All operands are fully NaN (either scalar NaNs or arrays of only
            # NaNs).
            return
        assert not numpy.all(rhsMask), "Should be guaranteed by prevoius two ifs."
        # If either operand is an array select just its not-NaN values.  Note
        # that these expressions are never True for scalar operands, because if
        # they are NaN then the numpy.all checks above will catch them.
        if numpy.any(lhsMask):
            lhs = lhs[numpy.logical_not(lhsMask)]
        if numpy.any(rhsMask):
            rhs = rhs[numpy.logical_not(rhsMask)]
    if not numpy.isfinite(lhs).all():
        testCase.fail("Non-finite values in lhs")
    if not numpy.isfinite(rhs).all():
        testCase.fail("Non-finite values in rhs")
    diff = lhs - rhs
    absDiff = numpy.abs(lhs - rhs)
    if rtol is not None:
        if relTo is None:
            relTo = numpy.maximum(numpy.abs(lhs), numpy.abs(rhs))
        else:
            relTo = numpy.abs(relTo)
        bad = absDiff > rtol * relTo
        if atol is not None:
            bad = numpy.logical_and(bad, absDiff > atol)
    else:
        if atol is None:
            raise ValueError("rtol and atol cannot both be None")
        bad = absDiff > atol
    failed = numpy.any(bad)
    if invert:
        failed = not failed
        bad = numpy.logical_not(bad)
        cmpStr = "=="
        failStr = "are the same"
    else:
        cmpStr = "!="
        failStr = "differ"
    errMsg = []
    if failed:
        if numpy.isscalar(bad):
            if rtol is None:
                errMsg = [f"{lhs} {cmpStr} {rhs}; diff={absDiff} with atol={atol}"]
            elif atol is None:
                errMsg = [f"{lhs} {cmpStr} {rhs}; diff={absDiff}/{relTo}={absDiff / relTo} with rtol={rtol}"]
            else:
                errMsg = [
                    f"{lhs} {cmpStr} {rhs}; diff={absDiff}/{relTo}={absDiff / relTo} "
                    f"with rtol={rtol}, atol={atol}"
                ]
        else:
            errMsg = [f"{bad.sum()}/{bad.size} elements {failStr} with rtol={rtol}, atol={atol}"]
            if plotOnFailure:
                if len(lhs.shape) != 2 or len(rhs.shape) != 2:
                    raise ValueError("plotOnFailure is only valid for 2-d arrays")
                try:
                    plotImageDiff(lhs, rhs, bad, diff=diff, plotFileName=plotFileName)
                except ImportError:
                    errMsg.append("Failure plot requested but matplotlib could not be imported.")
            if printFailures:
                # Make sure everything is an array if any of them are, so we
                # can treat them the same (diff and absDiff are arrays if
                # either rhs or lhs is), and we don't get here if neither is.
                if numpy.isscalar(relTo):
                    relTo = numpy.ones(bad.shape, dtype=float) * relTo
                if numpy.isscalar(lhs):
                    lhs = numpy.ones(bad.shape, dtype=float) * lhs
                if numpy.isscalar(rhs):
                    rhs = numpy.ones(bad.shape, dtype=float) * rhs
                if rtol is None:
                    for a, b, diff in zip(lhs[bad], rhs[bad], absDiff[bad]):
                        errMsg.append(f"{a} {cmpStr} {b} (diff={diff})")
                else:
                    for a, b, diff, rel in zip(lhs[bad], rhs[bad], absDiff[bad], relTo[bad]):
                        errMsg.append(f"{a} {cmpStr} {b} (diff={diff}/{rel}={diff / rel})")

    if msg is not None:
        errMsg.append(msg)
    testCase.assertFalse(failed, msg="\n".join(errMsg))


@inTestCase
def assertFloatsNotEqual(
    testCase: unittest.TestCase,
    lhs: float | numpy.ndarray,
    rhs: float | numpy.ndarray,
    **kwds: Any,
) -> None:
    """Fail a test if the given floating point values are equal to within the
    given tolerances.

    See `~lsst.utils.tests.assertFloatsAlmostEqual` (called with
    ``rtol=atol=0``) for more information.

    Parameters
    ----------
    testCase : `unittest.TestCase`
        Instance the test is part of.
    lhs : scalar or array-like
        LHS value(s) to compare; may be a scalar or array-like of any
        dimension.
    rhs : scalar or array-like
        RHS value(s) to compare; may be a scalar or array-like of any
        dimension.
    **kwds : `~typing.Any`
        Keyword parameters forwarded to `assertFloatsAlmostEqual`.

    Raises
    ------
    AssertionError
        The values are almost equal.
    """
    return assertFloatsAlmostEqual(testCase, lhs, rhs, invert=True, **kwds)


@inTestCase
def assertFloatsEqual(
    testCase: unittest.TestCase,
    lhs: float | numpy.ndarray,
    rhs: float | numpy.ndarray,
    **kwargs: Any,
) -> None:
    """
    Assert that lhs == rhs (both numeric types, whether scalar or array).

    See `~lsst.utils.tests.assertFloatsAlmostEqual` (called with
    ``rtol=atol=0``) for more information.

    Parameters
    ----------
    testCase : `unittest.TestCase`
        Instance the test is part of.
    lhs : scalar or array-like
        LHS value(s) to compare; may be a scalar or array-like of any
        dimension.
    rhs : scalar or array-like
        RHS value(s) to compare; may be a scalar or array-like of any
        dimension.
    **kwargs : `~typing.Any`
        Keyword parameters forwarded to `assertFloatsAlmostEqual`.

    Raises
    ------
    AssertionError
        The values are not equal.
    """
    return assertFloatsAlmostEqual(testCase, lhs, rhs, rtol=0, atol=0, **kwargs)


def _settingsIterator(settings: dict[str, Sequence[Any]]) -> Iterator[dict[str, Any]]:
    """Return an iterator for the provided test settings

    Parameters
    ----------
    settings : `dict` (`str`: iterable)
        Lists of test parameters. Each should be an iterable of the same
        length. If a string is provided as an iterable, it will be converted
        to a list of a single string.

    Raises
    ------
    AssertionError
        If the ``settings`` are not of the same length.

    Yields
    ------
    parameters : `dict` (`str`: anything)
        Set of parameters.
    """
    for name, values in settings.items():
        if isinstance(values, str):
            # Probably meant as a single-element string, rather than an
            # iterable of chars.
            settings[name] = [values]
    num = len(next(iter(settings.values())))  # Number of settings
    for name, values in settings.items():
        assert len(values) == num, f"Length mismatch for setting {name}: {len(values)} vs {num}"
    for ii in range(num):
        values = [settings[kk][ii] for kk in settings]
        yield dict(zip(settings, values))


def classParameters(**settings: Sequence[Any]) -> Callable:
    """Class decorator for generating unit tests.

    This decorator generates classes with class variables according to the
    supplied ``settings``.

    Parameters
    ----------
    **settings : `dict` (`str`: iterable)
        The lists of test parameters to set as class variables in turn. Each
        should be an iterable of the same length.

    Examples
    --------
    ::

        @classParameters(foo=[1, 2], bar=[3, 4])
        class MyTestCase(unittest.TestCase): ...

    will generate two classes, as if you wrote::

        class MyTestCase_1_3(unittest.TestCase):
            foo = 1
            bar = 3
            ...


        class MyTestCase_2_4(unittest.TestCase):
            foo = 2
            bar = 4
            ...

    Note that the values are embedded in the class name.
    """

    def decorator(cls: type) -> None:
        module = sys.modules[cls.__module__].__dict__
        for params in _settingsIterator(settings):
            name = f"{cls.__name__}_{'_'.join(str(vv) for vv in params.values())}"
            bindings = dict(cls.__dict__)
            bindings.update(params)
            module[name] = type(name, (cls,), bindings)

    return decorator


def methodParameters(**settings: Sequence[Any]) -> Callable:
    """Iterate over supplied settings to create subtests automatically.

    This decorator iterates over the supplied settings, using
    ``TestCase.subTest`` to communicate the values in the event of a failure.

    Parameters
    ----------
    **settings : `dict` (`str`: iterable)
        The lists of test parameters. Each should be an iterable of the same
        length.

    Examples
    --------
    .. code-block:: python

        @methodParameters(foo=[1, 2], bar=[3, 4])
        def testSomething(self, foo, bar): ...

    will run:

    .. code-block:: python

        testSomething(foo=1, bar=3)
        testSomething(foo=2, bar=4)
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self: unittest.TestCase, *args: Any, **kwargs: Any) -> None:
            for params in _settingsIterator(settings):
                kwargs.update(params)
                with self.subTest(**params):
                    func(self, *args, **kwargs)

        return wrapper

    return decorator


def _cartesianProduct(settings: Mapping[str, Sequence[Any]]) -> Mapping[str, Sequence[Any]]:
    """Return the cartesian product of the settings.

    Parameters
    ----------
    settings : `dict` mapping `str` to `iterable`
        Parameter combinations.

    Returns
    -------
    product : `dict` mapping `str` to `iterable`
        Parameter combinations covering the cartesian product (all possible
        combinations) of the input parameters.

    Examples
    --------
    .. code-block:: python

        cartesianProduct({"foo": [1, 2], "bar": ["black", "white"]})

    will return:

    .. code-block:: python

        {"foo": [1, 1, 2, 2], "bar": ["black", "white", "black", "white"]}
    """
    product: dict[str, list[Any]] = {kk: [] for kk in settings}
    for values in itertools.product(*settings.values()):
        for kk, vv in zip(settings.keys(), values):
            product[kk].append(vv)
    return product


def classParametersProduct(**settings: Sequence[Any]) -> Callable:
    """Class decorator for generating unit tests.

    This decorator generates classes with class variables according to the
    cartesian product of the supplied ``settings``.

    Parameters
    ----------
    **settings : `dict` (`str`: iterable)
        The lists of test parameters to set as class variables in turn. Each
        should be an iterable.

    Examples
    --------
    .. code-block:: python

        @classParametersProduct(foo=[1, 2], bar=[3, 4])
        class MyTestCase(unittest.TestCase): ...

    will generate four classes, as if you wrote::

    .. code-block:: python

        class MyTestCase_1_3(unittest.TestCase):
            foo = 1
            bar = 3
            ...


        class MyTestCase_1_4(unittest.TestCase):
            foo = 1
            bar = 4
            ...


        class MyTestCase_2_3(unittest.TestCase):
            foo = 2
            bar = 3
            ...


        class MyTestCase_2_4(unittest.TestCase):
            foo = 2
            bar = 4
            ...

    Note that the values are embedded in the class name.
    """
    return classParameters(**_cartesianProduct(settings))


def methodParametersProduct(**settings: Sequence[Any]) -> Callable:
    """Iterate over cartesian product creating sub tests.

    This decorator iterates over the cartesian product of the supplied
    settings, using `~unittest.TestCase.subTest` to communicate the values in
    the event of a failure.

    Parameters
    ----------
    **settings : `dict` (`str`: iterable)
        The parameter combinations to test. Each should be an iterable.

    Examples
    --------
        @methodParametersProduct(foo=[1, 2], bar=["black", "white"])
        def testSomething(self, foo, bar):
            ...

    will run:

        testSomething(foo=1, bar="black")
        testSomething(foo=1, bar="white")
        testSomething(foo=2, bar="black")
        testSomething(foo=2, bar="white")
    """
    return methodParameters(**_cartesianProduct(settings))


@contextlib.contextmanager
def temporaryDirectory() -> Iterator[str]:
    """Context manager that creates and destroys a temporary directory.

    The difference from `tempfile.TemporaryDirectory` is that this ignores
    errors when deleting a directory, which may happen with some filesystems.

    Yields
    ------
    `str`
        Name of the temporary directory.
    """
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    shutil.rmtree(tmpdir, ignore_errors=True)
