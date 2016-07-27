#include <pybind11/pybind11.h>

#include "lsst/utils/Utils.h"

using namespace lsst::utils;

namespace py = pybind11;

PYBIND11_PLUGIN(_utils) {
    py::module mod("_utils", "Access to the classes from the utils utils library");

    mod.def("getPackageDir", getPackageDir);

    return mod.ptr();
}

