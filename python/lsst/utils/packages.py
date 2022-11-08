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
#
from __future__ import annotations

"""
Determine which packages are being used in the system and their versions
"""
import hashlib
import importlib
import io
import json
import logging
import os
import pickle
import re
import subprocess
import sys
import types
from collections.abc import Mapping
from functools import lru_cache
from typing import Any, Dict, Optional, Tuple, Type

import yaml

log = logging.getLogger(__name__)

__all__ = [
    "getVersionFromPythonModule",
    "getPythonPackages",
    "getEnvironmentPackages",
    "getCondaPackages",
    "Packages",
]


# Packages used at build-time (e.g., header-only)
BUILDTIME = set(["boost", "eigen", "tmv"])

# Python modules to attempt to load so we can try to get the version
# We do this because the version only appears to be available from python,
# but we use the library
PYTHON = set(["galsim"])

# Packages that don't seem to have a mechanism for reporting the runtime
# version.  We need to guess the version from the environment
ENVIRONMENT = set(["astrometry_net", "astrometry_net_data", "minuit2", "xpa"])


def getVersionFromPythonModule(module: types.ModuleType) -> str:
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
            version += " with " + " ".join("%s=%s" % (pkg, deps[pkg]) for pkg in sorted(buildtime))
    return str(version)


def getPythonPackages() -> Dict[str, str]:
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
    for module_name in PYTHON:
        try:
            importlib.import_module(module_name)
        except Exception:
            pass  # It's not available, so don't care

    packages = {"python": sys.version}
    # Not iterating with sys.modules.iteritems() because it's not atomic and
    # subject to race conditions
    moduleNames = list(sys.modules.keys())
    for name in moduleNames:
        module = sys.modules[name]
        try:
            ver = getVersionFromPythonModule(module)
        except Exception:
            continue  # Can't get a version from it, don't care

        # Remove "foo.bar.version" in favor of "foo.bar"
        # This prevents duplication when the __init__.py includes
        # "from .version import *"
        for ending in (".version", "._version"):
            if name.endswith(ending):
                name = name[: -len(ending)]
                if name in packages:
                    assert ver == packages[name]
            elif name in packages:
                assert ver == packages[name]

        # Use LSST package names instead of python module names
        # This matches the names we get from the environment (i.e., EUPS)
        # so we can clobber these build-time versions if the environment
        # reveals that we're not using the packages as-built.
        if "lsst" in name:
            name = name.replace("lsst.", "").replace(".", "_")

        packages[name] = ver

    return packages


_eups: Optional[Any] = None  # Singleton Eups object


@lru_cache(maxsize=1)
def getEnvironmentPackages(include_all: bool = False) -> Dict[str, str]:
    """Get products and their versions from the environment.

    Parameters
    ----------
    include_all : `bool`
        If `False` only returns locally-setup packages. If `True` all set
        up packages are returned with a version that includes any associated
        non-current tags.

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
    for these packages unless ``include_all`` is `True`.
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
    # XXX Should we just grab everything we can, rather than just a
    # predetermined set?
    packages = {prod.name: prod.version for prod in products if prod in ENVIRONMENT}

    # The string 'LOCAL:' (the value of Product.LocalVersionPrefix) in the
    # version name indicates uninstalled code, so the version could be
    # different than what's being reported by the runtime environment (because
    # we don't tend to run "scons" every time we update some python file,
    # and even if we did sconsUtils probably doesn't check to see if the repo
    # is clean).
    for prod in products:
        if not prod.version.startswith(Product.LocalVersionPrefix):
            if include_all:
                tags = {t for t in prod.tags if t != "current"}
                tag_msg = " (" + " ".join(tags) + ")" if tags else ""
                packages[prod.name] = prod.version + tag_msg
            continue
        ver = prod.version

        gitDir = os.path.join(prod.dir, ".git")
        if os.path.exists(gitDir):
            # get the git revision and an indication if the working copy is
            # clean
            revCmd = ["git", "--git-dir=" + gitDir, "--work-tree=" + prod.dir, "rev-parse", "HEAD"]
            diffCmd = [
                "git",
                "--no-pager",
                "--git-dir=" + gitDir,
                "--work-tree=" + prod.dir,
                "diff",
                "--patch",
            ]
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


@lru_cache(maxsize=1)
def getCondaPackages() -> Dict[str, str]:
    """Get products and their versions from the conda environment.

    Returns
    -------
    packages : `dict`
        Keys (type `str`) are product names; values (type `str`) are their
        versions.

    Notes
    -----
    Returns empty result if a conda environment is not in use or can not
    be queried.
    """
    try:
        from conda.cli.python_api import Commands, run_command
    except ImportError:
        return {}

    # Get the installed package list
    versions_json = run_command(Commands.LIST, "--json")
    packages = {pkg["name"]: pkg["version"] for pkg in json.loads(versions_json[0])}

    # Try to work out the conda environment name and include it as a fake
    # package. The "obvious" way of running "conda info --json" does give
    # access to the active_prefix but takes about 2 seconds to run.
    # The equivalent to the code above would be:
    #    info_json = run_command(Commands.INFO, "--json")
    # As a comporomise look for the env name in the path to the python
    # executable
    match = re.search(r"/envs/(.*?)/bin/", sys.executable)
    if match:
        packages["conda_env"] = match.group(1)

    return packages


class Packages(dict):
    """A table of packages and their versions.

    There are a few different types of packages, and their versions are
    collected in different ways:

    1. Installed Conda packages are obtained via the Conda API. Conda is
       not required.
    2. Python modules (e.g., afw, numpy; galsim is also in this group even
       though we only use it through the library, because no version
       information is currently provided through the library): we get their
       version from the ``__version__`` module variable. Note that this means
       that we're only aware of modules that have already been imported.
    3. Other packages provide no run-time accessible version information (e.g.,
       astrometry_net): we get their version from interrogating the
       environment.  Currently, that means EUPS; if EUPS is replaced or dropped
       then we'll need to consider an alternative means of getting this version
       information.
    4. Local versions of packages (a non-installed EUPS package, selected with
       ``setup -r /path/to/package``): we identify these through the
       environment (EUPS again) and use as a version the path supplemented with
       the ``git`` SHA and, if the git repo isn't clean, an MD5 of the diff.

    These package versions are collected and stored in a Packages object, which
    provides useful comparison and persistence features.

    Example usage:

    .. code-block:: python

        from lsst.utils.packages import Packages
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
    This is a wrapper around a dict with some convenience methods.
    """

    formats = {".pkl": "pickle", ".pickle": "pickle", ".yaml": "yaml", ".json": "json"}

    def __setstate__(self, state: Dict[str, Any]) -> None:
        # This only seems to be called for old pickle files where
        # the data was stored in _packages.
        self.update(state["_packages"])

    @classmethod
    def fromSystem(cls) -> Packages:
        """Construct a `Packages` by examining the system.

        Determine packages by examining python's `sys.modules`, conda
        libraries and EUPS. EUPS packages take precedence over conda and
        general python packages.

        Returns
        -------
        packages : `Packages`
            All version package information that could be obtained.
        """
        packages = {}
        packages.update(getPythonPackages())
        packages.update(getCondaPackages())
        packages.update(getEnvironmentPackages())  # Should be last, to override products with LOCAL versions
        return cls(packages)

    @classmethod
    def fromBytes(cls, data: bytes, format: str) -> Packages:
        """Construct the object from a byte representation.

        Parameters
        ----------
        data : `bytes`
            The serialized form of this object in bytes.
        format : `str`
            The format of those bytes. Can be ``yaml``, ``json``, or
            ``pickle``.

        Returns
        -------
        packages : `Packages`
            The package information read from the input data.
        """
        if format == "pickle":
            file = io.BytesIO(data)
            new = _BackwardsCompatibilityUnpickler(file).load()
        elif format == "yaml":
            new = yaml.load(data, Loader=yaml.SafeLoader)
        elif format == "json":
            new = cls(json.loads(data))
        else:
            raise ValueError(f"Unexpected serialization format given: {format}")
        if not isinstance(new, cls):
            raise TypeError(f"Extracted object of class '{type(new)}' but expected '{cls}'")
        return new

    @classmethod
    def read(cls, filename: str) -> Packages:
        """Read packages from filename.

        Parameters
        ----------
        filename : `str`
            Filename from which to read. The format is determined from the
            file extension.  Currently support ``.pickle``, ``.pkl``,
            ``.json``, and ``.yaml``.

        Returns
        -------
        packages : `Packages`
            The packages information read from the file.
        """
        _, ext = os.path.splitext(filename)
        if ext not in cls.formats:
            raise ValueError(f"Format from {ext} extension in file {filename} not recognized")
        with open(filename, "rb") as ff:
            # We assume that these classes are tiny so there is no
            # substantive memory impact by reading the entire file up front
            data = ff.read()
        return cls.fromBytes(data, cls.formats[ext])

    def toBytes(self, format: str) -> bytes:
        """Convert the object to a serialized bytes form using the
        specified format.

        Parameters
        ----------
        format : `str`
            Format to use when serializing. Can be ``yaml``, ``json``,
            or ``pickle``.

        Returns
        -------
        data : `bytes`
            Byte string representing the serialized object.
        """
        if format == "pickle":
            return pickle.dumps(self)
        elif format == "yaml":
            return yaml.dump(self).encode("utf-8")
        elif format == "json":
            return json.dumps(self).encode("utf-8")
        else:
            raise ValueError(f"Unexpected serialization format requested: {format}")

    def write(self, filename: str) -> None:
        """Write to file.

        Parameters
        ----------
        filename : `str`
            Filename to which to write. The format of the data file
            is determined from the file extension. Currently supports
            ``.pickle``, ``.json``, and ``.yaml``
        """
        _, ext = os.path.splitext(filename)
        if ext not in self.formats:
            raise ValueError(f"Format from {ext} extension in file {filename} not recognized")
        with open(filename, "wb") as ff:
            # Assumes that the bytes serialization of this object is
            # relatively small.
            ff.write(self.toBytes(self.formats[ext]))

    def __str__(self) -> str:
        ss = "%s({\n" % self.__class__.__name__
        # Sort alphabetically by module name, for convenience in reading
        ss += ",\n".join(f"{prod!r}:{self[prod]!r}" for prod in sorted(self))
        ss += ",\n})"
        return ss

    def __repr__(self) -> str:
        # Default repr() does not report the class name.
        return f"{self.__class__.__name__}({super().__repr__()})"

    def extra(self, other: Mapping) -> Dict[str, str]:
        """Get packages in self but not in another `Packages` object.

        Parameters
        ----------
        other : `Packages` or `Mapping`
            Other packages to compare against.

        Returns
        -------
        extra : `dict`
            Extra packages. Keys (type `str`) are package names; values
            (type `str`) are their versions.
        """
        return {pkg: self[pkg] for pkg in self.keys() - other.keys()}

    def missing(self, other: Mapping) -> Dict[str, str]:
        """Get packages in another `Packages` object but missing from self.

        Parameters
        ----------
        other : `Packages`
            Other packages to compare against.

        Returns
        -------
        missing : `dict` [`str`, `str`]
            Missing packages. Keys (type `str`) are package names; values
            (type `str`) are their versions.
        """
        return {pkg: other[pkg] for pkg in other.keys() - self.keys()}

    def difference(self, other: Mapping) -> Dict[str, Tuple[str, str]]:
        """Get packages in symmetric difference of self and another `Packages`
        object.

        Parameters
        ----------
        other : `Packages`
            Other packages to compare against.

        Returns
        -------
        difference : `dict` [`str`, `tuple` [`str`, `str`]]
            Packages in symmetric difference.  Keys (type `str`) are package
            names; values (type `tuple`[`str`, `str`]) are their versions.
        """
        return {pkg: (self[pkg], other[pkg]) for pkg in self.keys() & other.keys() if self[pkg] != other[pkg]}


class _BackwardsCompatibilityUnpickler(pickle.Unpickler):
    """Replacement for the default unpickler.

    It is required so that users of this API can read pickle files
    created when the `~lsst.utils.packages.Packages` class was in a different
    package and known as ``lsst.base.Packages``. If this unpickler is being
    used then we know for sure that we must return a
    `~lsst.utils.packages.Packages` instance.
    """

    def find_class(self, module: str, name: str) -> Type:
        """Return the class that should be used for unpickling.

        This is always known to be the class in this package.
        """
        return Packages


# Register YAML representers


def pkg_representer(dumper: yaml.Dumper, data: Any) -> yaml.MappingNode:
    """Represent Packages as a simple dict"""
    return dumper.represent_mapping("lsst.utils.packages.Packages", data, flow_style=None)


yaml.add_representer(Packages, pkg_representer)


def pkg_constructor(loader: yaml.constructor.SafeConstructor, node: yaml.Node) -> Any:
    yield Packages(loader.construct_mapping(node, deep=True))  # type: ignore


for loader in (yaml.Loader, yaml.CLoader, yaml.UnsafeLoader, yaml.SafeLoader, yaml.FullLoader):
    yaml.add_constructor("lsst.utils.packages.Packages", pkg_constructor, Loader=loader)

    # Register the old name with YAML.
    yaml.add_constructor("lsst.base.Packages", pkg_constructor, Loader=loader)
