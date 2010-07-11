// -*- lsst-c++ -*-

/* 
 * LSST Data Management System
 * Copyright 2008, 2009, 2010 LSST Corporation.
 * 
 * This product includes software developed by the
 * LSST Project (http://www.lsst.org/).
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the LSST License Statement and 
 * the GNU General Public License along with this program.  If not, 
 * see <http://www.lsstcorp.org/LegalNotices/>.
 */
 
%define utils_DOCSTRING
"
Access to useful Utility classes.
"
%enddef

%feature("autodoc", "1");
%module(package="lsst.utils", docstring=utils_DOCSTRING) utilsLib

%{
#include "lsst/utils/Demangle.h"
#include "lsst/utils/Utils.h"
#include "lsst/utils/RaDecStr.h"
%}

%include "../p_lsstSwig.i"
%lsst_exceptions();
%include "lsst/utils/Demangle.h"
%include "lsst/utils/Utils.h"
%include "lsst/utils/RaDecStr.h"


%pythoncode %{
import re

def version(HeadURL = r"$HeadURL: svn+ssh://svn.lsstcorp.org/DMS/utils/trunk/python/lsst/utils.i $",
            ProductName=None):
    """
    Return a product name and version string, given a HeadURL string.
    If a different version is setup in eups, include it in the return string.
    """

    version_svn = guessSvnVersion(HeadURL)

    if not ProductName:
        # Guess the package name from HeadURL by extracting directory components
        # between DMS and trunk/branches/tickets/tags
        try:
            m = re.match(r".*/DMS/(.*)/(?:branches|tags|tickets|trunk)/.*", HeadURL)
            ProductName = m.group(1).replace('/','_')
        except:
            return "unknown product " + version_svn
    try:
        import eups
    except ImportError:
        pass
    else:
        try:
            version_eups = eups.Eups().findSetupVersion(ProductName)[0]
        except:
            version_eups = None
        if (version_eups and version_eups != version_svn): 
            return "%s %s (setup: %s)" % (ProductName, version_svn, version_eups)
    return "%s %s" % (ProductName, version_svn)

%}

