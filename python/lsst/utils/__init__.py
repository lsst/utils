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

from . import _utils
import lsst.bputils

lsst.bputils.rescope(_utils, globals(), ignore=())

def version(
    HeadURL = r"$HeadURL: svn+ssh://svn.lsstcorp.org/DMS/utils/trunk/python/lsst/__init__.i $",
    productName=None):
    """Return productName's version given a HeadURL string. If a different version is setup, return that too

N.b. you need to tell svn to expand that HeadURL in the first place!
"""

    version_eups = "(unknown)"
    version_svn = guessSvnVersion(HeadURL)

    if productName:
        try:
            import eups
        except ImportError:
            pass
        else:
            try:
                version_eups = eups.getSetupVersion(productName)
            except AttributeError:
                pass

    if version_eups == version_svn:
        return version_svn
    else:
        return "%s (setup: %s)" % (version_svn, version_eups)
