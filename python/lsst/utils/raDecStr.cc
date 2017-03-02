#include "pybind11/pybind11.h"

#include "lsst/utils/RaDecStr.h"

namespace py = pybind11;
using namespace pybind11::literals;

namespace lsst {
namespace utils {

PYBIND11_PLUGIN(raDecStr) {
    py::module mod("raDecStr");

    mod.def("raRadToStr", raRadToStr);
    mod.def("decRadToStr", decRadToStr);
    mod.def("raDegToStr", raDegToStr);
    mod.def("decDegToStr", decDegToStr);
    mod.def("raDecRadToStr", raDecRadToStr);
    mod.def("raDecDegToStr", raDecDegToStr);
    mod.def("raStrToRad", raStrToRad,
        "raStr"_a, "delimiter"_a=":");
    mod.def("raStrToDeg", raStrToDeg,
        "raStr"_a, "delimiter"_a=":");
    mod.def("decStrToRad", decStrToRad,
        "raStr"_a, "delimiter"_a=":");
    mod.def("decStrToDeg", decStrToDeg,
        "raStr"_a, "delimiter"_a=":");

    return mod.ptr();
}

}  // utils
}  // lsst

