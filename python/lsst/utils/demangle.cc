#include "pybind11/pybind11.h"

#include "lsst/utils/Demangle.h"

namespace py = pybind11;

namespace lsst {
namespace utils {

PYBIND11_MODULE(demangle, mod) {
    mod.def("demangleType", demangleType);
}

}  // utils
}  // lsst
