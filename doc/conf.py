"""Sphinx configuration file for an LSST stack package.

This configuration only affects single-package Sphinx documenation builds.
"""
# ruff: noqa: F403, F405

from documenteer.conf.guide import *

exclude_patterns.append("changes/*")

intersphinx_mapping["astropy"] = ("https://docs.astropy.org/en/stable", None)
intersphinx_mapping["python"] = ("https://docs.python.org/3", None)
