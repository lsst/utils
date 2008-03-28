// -*- lsst-c++ -*-
%define utils_DOCSTRING
"
Access to useful Utility classes in the mwi library.
"
%enddef

%feature("autodoc", "1");
%module(package="lsst.mwi", docstring=utils_DOCSTRING) utils

%{
#   include <fstream>
#   include <exception>
#   include <map>
#   include "lsst/mwi/utils/Demangle.h"
#   include "lsst/mwi/utils/Trace.h"
#   include "lsst/mwi/utils/Utils.h"
%}

%inline %{
namespace lsst { namespace mwi { namespace utils { } } }
    
using namespace lsst;
using namespace lsst::mwi::utils;
%}

%init %{
%}

%include "p_lsstSwig.i"
%include "lsst/mwi/utils/Utils.h"

%pythoncode %{

def version(HeadURL = r"$HeadURL$"):
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

/******************************************************************************/
// Trace
%ignore Trace(const std::string&, const int, const std::string&, va_list ap);
%include "lsst/mwi/utils/Trace.h"

/******************************************************************************/
// Local Variables: ***
// eval: (setq indent-tabs-mode nil) ***
// End: ***
