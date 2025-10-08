"""Sphinx configuration file for an LSST stack package.

This configuration only affects single-package Sphinx documenation builds.
"""

from documenteer.conf.pipelinespkg import *  # noqa: F403, import *

project = "utils"
html_theme_options["logotext"] = project  # noqa: F405, unknown name
html_title = project
html_short_title = project
doxylink = {}
exclude_patterns = ["changes/*"]
nitpick_ignore_regex = [
    ("py:.*", r"lsst\..*"),  # Ignore warnings from links to other lsst packages.
    ("py:.*", "cProfile.Profile"),  # Link does not resolve to py3 docs.
    ("py:class", "a set-like.*"),  # collections.abc.Mapping inheritance.
    ("py:class", "a shallow copy.*"),  # collections.abc.Mapping inheritance.
    ("py:class", r"None\.  .*"),  # collections.abc.Mapping inheritance.
    ("py:class", "an object providing.*"),  # collections.abc.Mapping inheritance.
]
nitpick_ignore = [
    ("py:class", "module"),  # Sphinx has problems with types.ModuleType.
    ("py:obj", "logging.DEBUG"),  # Python 3 constant can not be found.
    ("py:class", "unittest.case.TestCase"),  # Sphinx can not see TestCase.
    ("py:obj", "deprecated.sphinx.deprecated"),  # No intersphinx for deprecated package.
    ("py:class", "LsstLoggers"),  # Sphinx does not understand type aliases
    ("py:obj", "structlog"),  # structlog does not have intersphinx mapping.
]
