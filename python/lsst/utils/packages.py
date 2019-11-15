# This file is part of base.
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
"""
Determine which packages are being used in the system and their versions
"""
import os
import sys
import hashlib
import importlib
import subprocess
import logging
import pickle as pickle
from collections.abc import Mapping

from .versions import getRuntimeVersions

log = logging.getLogger(__name__)

__all__ = ["getVersionFromPythonModule", "getPythonPackages", "getEnvironmentPackages", "Packages"]


# Packages used at build-time (e.g., header-only)
BUILDTIME = set(["boost", "eigen", "tmv"])

# Python modules to attempt to load so we can try to get the version
# We do this because the version only appears to be available from python, but we use the library
PYTHON = set(["galsim"])

# Packages that don't seem to have a mechanism for reporting the runtime version
# We need to guess the version from the environment
ENVIRONMENT = set(["astrometry_net", "astrometry_net_data", "minuit2", "xpa"])


def getVersionFromPythonModule(module):
    """Determine the version of a python module.

    Parameters
    ----------
    module : `module`
        Module for which to get version.

    Returns
    -------
    version : `str`

    Raises
    ------
    AttributeError
        Raised if __version__ attribute is not set.

    Notes
    -----
    We supplement the version with information from the
    ``__dependency_versions__`` (a specific variable set by LSST's
    `~lsst.sconsUtils` at build time) only for packages that are typically
    used only at build-time.
    """
    version = module.__version__
    if hasattr(module, "__dependency_versions__"):
        # Add build-time dependencies
        deps = module.__dependency_versions__
        buildtime = BUILDTIME & set(deps.keys())
        if buildtime:
            version += " with " + " ".join("%s=%s" % (pkg, deps[pkg])
                                           for pkg in sorted(buildtime))
    return version


def getPythonPackages():
    """Get imported python packages and their versions.

    Returns
    -------
    packages : `dict`
        Keys (type `str`) are package names; values (type `str`) are their
        versions.

    Notes
    -----
    We wade through `sys.modules` and attempt to determine the version for each
    module.  Note, therefore, that we can only report on modules that have
    *already* been imported.

    We don't include any module for which we cannot determine a version.
    """
    # Attempt to import libraries that only report their version in python
    for module in PYTHON:
        try:
            importlib.import_module(module)
        except Exception:
            pass  # It's not available, so don't care

    packages = {"python": sys.version}
    # Not iterating with sys.modules.iteritems() because it's not atomic and subject to race conditions
    moduleNames = list(sys.modules.keys())
    for name in moduleNames:
        module = sys.modules[name]
        try:
            ver = getVersionFromPythonModule(module)
        except Exception:
            continue  # Can't get a version from it, don't care

        # Remove "foo.bar.version" in favor of "foo.bar"
        # This prevents duplication when the __init__.py includes "from .version import *"
        for ending in (".version", "._version"):
            if name.endswith(ending):
                name = name[:-len(ending)]
                if name in packages:
                    assert ver == packages[name]
            elif name in packages:
                assert ver == packages[name]

        # Use LSST package names instead of python module names
        # This matches the names we get from the environment (i.e., EUPS) so we can clobber these build-time
        # versions if the environment reveals that we're not using the packages as-built.
        if "lsst" in name:
            name = name.replace("lsst.", "").replace(".", "_")

        packages[name] = ver

    return packages


_eups = None  # Singleton Eups object


def getEnvironmentPackages():
    """Get products and their versions from the environment.

    Returns
    -------
    packages : `dict`
        Keys (type `str`) are product names; values (type `str`) are their
        versions.

    Notes
    -----
    We use EUPS to determine the version of certain products (those that don't
    provide a means to determine the version any other way) and to check if
    uninstalled packages are being used. We only report the product/version
    for these packages.
    """
    try:
        from eups import Eups
        from eups.Product import Product
    except ImportError:
        log.warning("Unable to import eups, so cannot determine package versions from environment")
        return {}

    # Cache eups object since creating it can take a while
    global _eups
    if not _eups:
        _eups = Eups()
    products = _eups.findProducts(tags=["setup"])

    # Get versions for things we can't determine via runtime mechanisms
    # XXX Should we just grab everything we can, rather than just a predetermined set?
    packages = {prod.name: prod.version for prod in products if prod in ENVIRONMENT}

    # The string 'LOCAL:' (the value of Product.LocalVersionPrefix) in the version name indicates uninstalled
    # code, so the version could be different than what's being reported by the runtime environment (because
    # we don't tend to run "scons" every time we update some python file, and even if we did sconsUtils
    # probably doesn't check to see if the repo is clean).
    for prod in products:
        if not prod.version.startswith(Product.LocalVersionPrefix):
            continue
        ver = prod.version

        gitDir = os.path.join(prod.dir, ".git")
        if os.path.exists(gitDir):
            # get the git revision and an indication if the working copy is clean
            revCmd = ["git", "--git-dir=" + gitDir, "--work-tree=" + prod.dir, "rev-parse", "HEAD"]
            diffCmd = ["git", "--no-pager", "--git-dir=" + gitDir, "--work-tree=" + prod.dir, "diff",
                       "--patch"]
            try:
                rev = subprocess.check_output(revCmd).decode().strip()
                diff = subprocess.check_output(diffCmd)
            except Exception:
                ver += "@GIT_ERROR"
            else:
                ver += "@" + rev
                if diff:
                    ver += "+" + hashlib.md5(diff).hexdigest()
        else:
            ver += "@NO_GIT"

        packages[prod.name] = ver
    return packages


class Packages:
    """A table of packages and their versions.

    There are a few different types of packages, and their versions are collected
    in different ways:

    1. Run-time libraries (e.g., cfitsio, fftw): we get their version from
       interrogating the dynamic library
    2. Python modules (e.g., afw, numpy; galsim is also in this group even though
       we only use it through the library, because no version information is
       currently provided through the library): we get their version from the
       ``__version__`` module variable. Note that this means that we're only aware
       of modules that have already been imported.
    3. Other packages provide no run-time accessible version information (e.g.,
       astrometry_net): we get their version from interrogating the environment.
       Currently, that means EUPS; if EUPS is replaced or dropped then we'll need
       to consider an alternative means of getting this version information.
    4. Local versions of packages (a non-installed EUPS package, selected with
       ``setup -r /path/to/package``): we identify these through the environment
       (EUPS again) and use as a version the path supplemented with the ``git``
       SHA and, if the git repo isn't clean, an MD5 of the diff.

    These package versions are collected and stored in a Packages object, which
    provides useful comparison and persistence features.

    Example usage:

    .. code-block:: python

        from lsst.base import Packages
        pkgs = Packages.fromSystem()
        print("Current packages:", pkgs)
        old = Packages.read("/path/to/packages.pickle")
        print("Old packages:", old)
        print("Missing packages compared to before:", pkgs.missing(old))
        print("Extra packages compared to before:", pkgs.extra(old))
        print("Different packages: ", pkgs.difference(old))
        old.update(pkgs)  # Include any new packages in the old
        old.write("/path/to/packages.pickle")

    Parameters
    ----------
    packages : `dict`
        A mapping {package: version} where both keys and values are type `str`.

    Notes
    -----
    This is essentially a wrapper around a dict with some conveniences.
    """

    def __init__(self, packages):
        assert isinstance(packages, Mapping)
        self._packages = packages
        self._names = set(packages.keys())

    @classmethod
    def fromSystem(cls):
        """Construct a `Packages` by examining the system.

        Determine packages by examining python's `sys.modules`, runtime
        libraries and EUPS.

        Returns
        -------
        packages : `Packages`
        """
        packages = {}
        packages.update(getPythonPackages())
        packages.update(getRuntimeVersions())
        packages.update(getEnvironmentPackages())  # Should be last, to override products with LOCAL versions
        return cls(packages)

    @classmethod
    def read(cls, filename):
        """Read packages from filename.

        Parameters
        ----------
        filename : `str`
            Filename from which to read.

        Returns
        -------
        packages : `Packages`
        """
        with open(filename, "rb") as ff:
            return pickle.load(ff)

    def write(self, filename):
        """Write to file.

        Parameters
        ----------
        filename : `str`
            Filename to which to write.
        """
        with open(filename, "wb") as ff:
            pickle.dump(self, ff)

    def __len__(self):
        return len(self._packages)

    def __str__(self):
        ss = "%s({\n" % self.__class__.__name__
        # Sort alphabetically by module name, for convenience in reading
        ss += ",\n".join("%s: %s" % (repr(prod), repr(self._packages[prod])) for
                         prod in sorted(self._names))
        ss += ",\n})"
        return ss

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, repr(self._packages))

    def __contains__(self, pkg):
        return pkg in self._packages

    def __iter__(self):
        return iter(self._packages)

    def update(self, other):
        """Update packages with contents of another set of packages.

        Parameters
        ----------
        other : `Packages`
            Other packages to merge with self.

        Notes
        -----
        No check is made to see if we're clobbering anything.
        """
        self._packages.update(other._packages)
        self._names.update(other._names)

    def extra(self, other):
        """Get packages in self but not in another `Packages` object.

        Parameters
        ----------
        other : `Packages`
            Other packages to compare against.

        Returns
        -------
        extra : `dict`
            Extra packages. Keys (type `str`) are package names; values
            (type `str`) are their versions.
        """
        return {pkg: self._packages[pkg] for pkg in self._names - other._names}

    def missing(self, other):
        """Get packages in another `Packages` object but missing from self.

        Parameters
        ----------
        other : `Packages`
            Other packages to compare against.

        Returns
        -------
        missing : `dict`
            Missing packages. Keys (type `str`) are package names; values
            (type `str`) are their versions.
        """
        return {pkg: other._packages[pkg] for pkg in other._names - self._names}

    def difference(self, other):
        """Get packages in symmetric difference of self and another `Packages`
        object.

        Parameters
        ----------
        other : `Packages`
            Other packages to compare against.

        Returns
        -------
        difference : `dict`
            Packages in symmetric difference.  Keys (type `str`) are package
            names; values (type `str`) are their versions.
        """
        return {pkg: (self._packages[pkg], other._packages[pkg]) for
                pkg in self._names & other._names if self._packages[pkg] != other._packages[pkg]}
