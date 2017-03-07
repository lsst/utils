#include "pybind11/pybind11.h"
#include "pybind11/stl.h"

#include <utility>

#include "lsst/utils/python.h"

namespace py = pybind11;
using namespace pybind11::literals;

namespace lsst {
namespace utils {
namespace python {

PYBIND11_PLUGIN(python) {
    py::module mod("python");

    // wrap cppIndex in order to make it easy to test
    mod.def("cppIndex", (std::size_t(*)(std::ptrdiff_t, std::ptrdiff_t))cppIndex, "size"_a, "i"_a);
    mod.def("cppIndex", (std::pair<std::size_t, std::size_t>(*)(std::ptrdiff_t, std::ptrdiff_t,
                                                                std::ptrdiff_t, std::ptrdiff_t))cppIndex,
            "size_i"_a, "size_j"_a, "i"_a, "j"_a);

    return mod.ptr();
}

}  // python
}  // utils
}  // lsst
