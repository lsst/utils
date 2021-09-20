#!/bin/sh

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

# Simple executable shell script.
# By default does nothing and exits with 0 status.
# with "-f" option, exits with a status of 1

while getopts "fh" opt; do
  case "$opt" in
  f)
    echo "Triggering bad exit status"
    exit 1
    ;;
  *)
    ;;
  esac
done

echo "Completing test script without error"
