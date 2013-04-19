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

"""Support code for running unit tests"""

import unittest
import numpy
try:
    import lsst.daf.base as dafBase
except ImportError:
    dafBase = None

import lsst.pex.exceptions as pexExcept
import os
import sys
import gc

try:
    type(memId0)
except NameError:
    memId0 = 0                          # ignore leaked blocks with IDs before memId0
    nleakPrintMax = 20                  # maximum number of leaked blocks to print

def init():
    global memId0
    if dafBase:
        memId0 = dafBase.Citizen_getNextMemId() # used by MemoryTestCase

def run(suite, exit=True):
    """Exit with the status code resulting from running the provided test suite"""

    if unittest.TextTestRunner().run(suite).wasSuccessful():
        status = 0
    else:
        status = 1

    if exit:
        sys.exit(status)
    else:
        return status

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
        
class MemoryTestCase(unittest.TestCase):
    """Check for memory leaks since memId0 was allocated"""
    def setUp(self):
        pass

    def testLeaks(self):
        """Check for memory leaks in the preceding tests"""
        if dafBase:
            gc.collect()
            global memId0, nleakPrintMax
            nleak = dafBase.Citizen_census(0, memId0)
            if nleak != 0:
                print "\n%d Objects leaked:" % dafBase.Citizen_census(0, memId0)

                if nleak <= nleakPrintMax:
                    print dafBase.Citizen_census(dafBase.cout, memId0)
                else:
                    census = dafBase.Citizen_census()
                    print "..."
                    for i in range(nleakPrintMax - 1, -1, -1):
                        print census[i].repr()

                self.fail("Leaked %d blocks" % dafBase.Citizen_census(0, memId0))

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

def findFileFromRoot(ifile):
    """Find file which is specified as a path relative to the toplevel directory;
    we start in $cwd and walk up until we find the file (or throw IOError if it doesn't exist)

    This is useful for running tests that may be run from <dir>/tests or <dir>"""
    
    if os.path.isfile(ifile):
        return ifile

    ofile = None
    file = ifile
    while file != "":
        dirname, basename = os.path.split(file)
        if ofile:
            ofile = os.path.join(basename, ofile)
        else:
            ofile = basename

        if os.path.isfile(ofile):
            return ofile

        file = dirname

    raise IOError, "Can't find %s" % ifile

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

class temporaryFile:
    """A class to be used with a with statement to ensure that a file is deleted
E.g.

with temporaryFile("foo.fits") as filename:
    image.writeFits(filename)
    readImage = Image(filename)
    """
    def __init__(self, filename):
        self.filename = filename

    def __enter__(self):
        return self.filename

    def __exit__(self, type, value, traceback):
        import os
        try:
            os.remove(self.filename)
        except OSError:
            pass

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

class TestCase(unittest.TestCase):
    """Subclass of unittest.TestCase that adds some custom assertions for
    convenience.
    """

def inTestCase(func):
    """A decorator to add a free function to our custom TestCase class, while also
    making it available as a free function.
    """
    setattr(TestCase, func.__name__, func)
    return func

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

@inTestCase
def assertRaisesLsstCpp(testcase, excClass, callableObj, *args, **kwargs):
    """
    Fail unless an LSST C++ exception of SWIG-wrapper class excClass
    is thrown by callableObj when invoked with arguments args and
    keywords arguments kwargs. If a different type of exception
    is thrown, it will not be caught, and the test case will be
    deemed to have suffered an error, exactly as for an
    unexpected exception.
    """
    try:
        callableObj(*args, **kwargs)
    except pexExcept.LsstCppException, e:
        if (isinstance(e.args[0], excClass)): return
    if hasattr(excClass,'__name__'): excName = excClass.__name__
    else: excName = str(excClass)
    raise testcase.failureException, "lsst.pex.exceptions.LsstCppException wrapping %s not raised" % excName

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

import functools
def debugger(*exceptions):
    """Decorator to enter the debugger when there's an uncaught exception

    To use, just slap a "@debugger()" on your function.

    You may provide specific exception classes to catch as arguments to
    the decorator function, e.g., "@debugger(RuntimeError, NotImplementedError)".
    This defaults to just 'AssertionError', for use on unittest.TestCase methods.

    Code provided by "Rosh Oxymoron" on StackOverflow:
    http://stackoverflow.com/questions/4398967/python-unit-testing-automatically-running-the-debugger-when-a-test-fails
    """
    if not exceptions:
        exceptions = (AssertionError, )
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except exceptions:
                import sys, pdb
                pdb.post_mortem(sys.exc_info()[2])
        return wrapper
    return decorator

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

@inTestCase
def assertClose(testCase, lhs, rhs, rtol=sys.float_info.epsilon, atol=sys.float_info.epsilon, relTo=None,
                printFailures=True, plotOnFailure=False, plotFileName=None, invert=False):
    """Highly-configurable floating point comparisons for scalars and arrays.

    The test assertion will fail if all elements lhs and rhs are not equal to within the tolerances
    specified by rtol and atol.  More precisely, the comparison is:

    abs(lhs - rhs) <= relTo*rtol OR abs(lhs - rhs) <= atol

    If rtol or atol is None, that term in the comparison is not performed at all.

    When not specified, relTo is the elementwise maximum of the absolute values of lhs and rhs.

    @param[in]  testCase       unittest.TestCase instance the test is part of
    @param[in]  lhs            LHS value(s) to compare; may be a scalar or a numpy array of any dimension
    @param[in]  rhs            RHS value(s) to compare; may be a scalar or a numpy array of any dimension
    @param[in]  rtol           Relative tolerance for comparison; defaults to double-precision epsilon.
    @param[in]  atol           Absolute tolerance for comparison; defaults to double-precision epsilon.
    @param[in]  relTo          Value to which comparison with rtol is relative.
    @param[in]  printFailures  Upon failure, print all inequal elements as part of the message.
    @param[in]  plotOnFailure  Upon failure, plot the originals and their residual with matplotlib.
                               Only 2-d arrays are supported.
    @param[in]  plotFileName   Filename to save the plot to.  If None, the plot will be displayed in a
                               a window.
    @param[in]  invert         If True, invert the comparison and fail only if any elements *are* equal.
                               Used to implement assertNotClose, which should generally be used instead
                               for clarity.
    """
    diff = lhs - rhs
    absDiff = numpy.abs(lhs - rhs)
    if rtol is not None:
        if relTo is None:
            relTo = numpy.maximum(numpy.abs(lhs), numpy.abs(rhs))
        else:
            relTo = numpy.abs(relTo)
        bad = absDiff > rtol*relTo
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
    msg = []
    if failed:
        if numpy.isscalar(bad):
            msg = ["%s %s %s; diff=%s/%s=%s with rtol=%s, atol=%s"
                   % (lhs, cmpStr, rhs, absDiff, relTo, absDiff/relTo, rtol, atol)]
        else:
            msg = ["%d/%d elements %s with rtol=%s, atol=%s"
                   % (bad.sum(), bad.size, failStr, rtol, atol)]
            if plotOnFailure:
                if len(lhs.shape) != 2 or len(rhs.shape) != 2:
                    raise ValueError("plotOnFailure is only valid for 2-d arrays")
                kwargs = dict(
                    )
                from matplotlib import pyplot
                pyplot.figure()
                xg, yg = numpy.meshgrid(numpy.arange(bad.shape[1]), numpy.arange(bad.shape[0]))
                badX = xg[bad]
                badY = yg[bad]
                vmin1 = numpy.minimum(numpy.min(lhs), numpy.min(rhs))
                vmax1 = numpy.maximum(numpy.max(lhs), numpy.max(rhs))
                vmin2 = numpy.min(diff)
                vmax2 = numpy.max(diff)
                for n, (image, title) in enumerate([(lhs, "lhs"), (rhs, "rhs"), (diff, "diff")]):
                    pyplot.subplot(2,3,n+1)
                    im1 = pyplot.imshow(image, cmap=pyplot.cm.gray, interpolation='nearest', origin='lower',
                                        vmin=vmin1, vmax=vmax1)
                    pyplot.plot(badX, badY, 'rx')
                    pyplot.axis("off")
                    pyplot.title(title)
                    pyplot.subplot(2,3,n+4)
                    im2 = pyplot.imshow(image, cmap=pyplot.cm.gray, interpolation='nearest', origin='lower',
                                        vmin=vmin2, vmax=vmax2)
                    pyplot.plot(badX, badY, 'rx')
                    pyplot.axis("off")
                    pyplot.title(title)
                pyplot.subplots_adjust(left=0.05, bottom=0.05, top=0.92, right=0.75, wspace=0.05, hspace=0.05)
                cax1 = pyplot.axes([0.8, 0.55, 0.05, 0.4])
                pyplot.colorbar(im1, cax=cax1)
                cax2 = pyplot.axes([0.8, 0.05, 0.05, 0.4])
                pyplot.colorbar(im2, cax=cax2)
                if plotFileName:
                    pyplot.savefig(plotFileName)
                else:
                    pyplot.show()
            if printFailures:
                if numpy.isscalar:
                    relTo = numpy.ones(bad.shape, dtype=float) * relTo
                for a, b, diff, rel in zip(lhs[bad], rhs[bad], absDiff[bad], relTo[bad]):
                    msg.append("%s %s %s (diff=%s/%s=%s)" % (a, cmpStr, b, diff, rel, diff/rel))
    testCase.assertFalse(failed, msg="\n".join(msg))

@inTestCase
def assertNotClose(testCase, lhs, rhs, **kwds):
    """Fail a test if the given floating point values are completely equal to within the given tolerances.

    See assertClose for more information.
    """
    return assertClose(testCase, lhs, rhs, invert=True, **kwds)
