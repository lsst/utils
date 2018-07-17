#include "pybind11/pybind11.h"

#include "lsst/utils/Utils.h"

namespace py = pybind11;

namespace lsst {
namespace utils {

PYBIND11_MODULE(utils, mod) {
    mod.def("getPackageDir", getPackageDir);
}

}  // utils
}  // lsst
