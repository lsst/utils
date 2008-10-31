// -*- lsst-c++ -*-
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
%}

#define NO_SWIG_LSST_EXCEPTIONS
%include "../p_lsstSwig.i"
%include "lsst/utils/Demangle.h"
%include "lsst/utils/Utils.h"

%pythoncode %{

def version(HeadURL = r"$HeadURL: svn+ssh://svn.lsstcorp.org/DMS/utils/trunk/python/lsst/utils.i $"):
    """Return a version given a HeadURL string.  If a different version's setup, return that too"""

    version_svn = guessSvnVersion(HeadURL)

    try:
        import eups
    except ImportError:
        return version_svn
    else:
        try:
            version_eups = eups.setup("fw")
        except AttributeError:
            return version_svn

    if version_eups == version_svn:
        return version_svn
    else:
        return "%s (setup: %s)" % (version_svn, version_eups)

%}

