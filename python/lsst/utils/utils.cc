#include "pybind11/pybind11.h"

#include "lsst/utils/Utils.h"

namespace py = pybind11;

namespace lsst {
namespace utils {

PYBIND11_PLUGIN(utils) {
    py::module mod("utils");

    mod.def("getPackageDir", getPackageDir);

    return mod.ptr();
}

}  // utils
}  // lsst
