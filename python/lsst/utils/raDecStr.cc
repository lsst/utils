#include <pybind11/pybind11.h>

#include "lsst/utils/RaDecStr.h"

using namespace lsst::utils;

namespace py = pybind11;

PYBIND11_PLUGIN(_raDecStr) {
    py::module mod("_raDecStr", "Access to the classes from the utils raDecStr library");

    mod.def("raRadToStr", raRadToStr);
    mod.def("decRadToStr", decRadToStr);
    mod.def("raDegToStr", raDegToStr);
    mod.def("decDegToStr", decDegToStr);
    mod.def("raDecRadToStr", raDecRadToStr);
    mod.def("raDecDegToStr", raDecDegToStr);
    mod.def("raStrToRad", raStrToRad,
        py::arg("raStr"), py::arg("delimiter")=":");
    mod.def("raStrToDeg", raStrToDeg,
        py::arg("raStr"), py::arg("delimiter")=":");
    mod.def("decStrToRad", decStrToRad,
        py::arg("raStr"), py::arg("delimiter")=":");
    mod.def("decStrToDeg", decStrToDeg,
        py::arg("raStr"), py::arg("delimiter")=":");

    return mod.ptr();
}

