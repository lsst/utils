#include "pybind11/pybind11.h"

#include "lsst/utils/python.h"

namespace lsst {
namespace utils {

void wrapBacktrace(python::WrapperCollection & wrappers);
void wrapUtils(python::WrapperCollection & wrappers);
void wrapDemangle(python::WrapperCollection & wrappers);

PYBIND11_MODULE(_utils, mod) {
    python::WrapperCollection wrappers(mod, "_utils");
    {
        auto backtraceWrappers = wrappers.makeSubmodule("backtrace");
        wrapBacktrace(backtraceWrappers);
        wrappers.collectSubmodule(std::move(backtraceWrappers));
    }
    wrapUtils(wrappers);
    wrapDemangle(wrappers);
    wrappers.finish();
}

}  // utils
}  // lsst
