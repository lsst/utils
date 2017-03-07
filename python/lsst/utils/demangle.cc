#include "pybind11/pybind11.h"

#include "lsst/utils/Demangle.h"

namespace py = pybind11;

namespace lsst {
namespace utils {

PYBIND11_PLUGIN(demangle) {
    py::module mod("demangle");

    mod.def("demangleType", demangleType);

    return mod.ptr();
}

}  // utils
}  // lsst
