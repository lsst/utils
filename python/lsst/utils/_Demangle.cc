#include "pybind11/pybind11.h"

#include "lsst/utils/python.h"
#include "lsst/utils/Demangle.h"

namespace py = pybind11;

namespace lsst {
namespace utils {

void wrapDemangle(python::WrapperCollection & wrappers) {
    wrappers.wrapFunctions(
        [](auto & mod) {
            mod.def("demangleType", demangleType);
        }
    );
}

}  // utils
}  // lsst
