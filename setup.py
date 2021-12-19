#!/usr/bin/env python

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

import os

from setuptools import setup

version = "0.1.0"
with open("./python/lsst/utils/version.py", "w") as f:
    print(
        f"""
__all__ = ("__version__", )
__version__ = '{version}'""",
        file=f,
    )

# read the contents of our README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

setup(version=f"{version}", long_description=long_description, long_description_content_type="text/rst")
