#include <pybind11/pybind11.h>

#include "lsst/utils/Demangle.h"

using namespace lsst::utils;

namespace py = pybind11;

PYBIND11_PLUGIN(_demangle) {
    py::module mod("_demangle", "Access to the classes from the utils demangle library");

    mod.def("demangleType", demangleType);

    return mod.ptr();
}

