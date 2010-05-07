#include <boost/python.hpp>
#include "lsst/utils/Demangle.h"
#include "lsst/utils/RaDecStr.h"
#include "lsst/utils/Utils.h"

namespace bp = boost::python;

namespace lsst { namespace utils {

static bp::str pyGuessSvnVersion(std::string const& headURL) {
    std::string result;
    guessSvnVersion(headURL, result);
    return bp::str(result);
}

}}

BOOST_PYTHON_MODULE(utilsLib) {
    bp::import("lsst.pex.exceptions");
    bp::def("demangleType", &lsst::utils::demangleType);
    bp::def("raRadToStr", &lsst::utils::raRadToStr);
    bp::def("decRadToStr", &lsst::utils::decRadToStr);
    bp::def("raDegToStr", &lsst::utils::raDegToStr);
    bp::def("decDegToStr", &lsst::utils::decDegToStr);
    bp::def("raDecRadToStr", &lsst::utils::raDecRadToStr);
    bp::def("raDecDegToStr", &lsst::utils::raDecDegToStr);
    bp::def("raStrToRad", &lsst::utils::raStrToRad, (bp::arg("raStr"), bp::arg("delimiter")=":"));
    bp::def("raStrToDeg", &lsst::utils::raStrToDeg, (bp::arg("raStr"), bp::arg("delimiter")=":"));
    bp::def("decStrToRad", &lsst::utils::decStrToRad, (bp::arg("decStr"), bp::arg("delimiter")=":"));
    bp::def("decStrToDeg", &lsst::utils::decStrToDeg, (bp::arg("decStr"), bp::arg("delimiter")=":"));
    bp::def("guessSvnVersion", &lsst::utils::pyGuessSvnVersion);
    bp::def("productDir", &lsst::utils::eups::productDir, (bp::arg("product"), bp::arg("version")="setup"));
}
