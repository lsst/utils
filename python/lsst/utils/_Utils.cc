#include "pybind11/pybind11.h"

#include "lsst/utils/python.h"
#include "lsst/utils/Utils.h"

namespace lsst {
namespace utils {

void wrapUtils(python::WrapperCollection & wrappers) {
    wrappers.wrapFunctions(
        [](auto & mod) {
            mod.def("getPackageDir", getPackageDir);
        }
    );
}

}  // utils
}  // lsst
