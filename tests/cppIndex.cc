/*
 * Developed for the LSST Data Management System.
 * This product includes software developed by the LSST Project
 * (https://www.lsst.org).
 * See the COPYRIGHT file at the top-level directory of this distribution
 * for details of code ownership.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

#include "pybind11/pybind11.h"
#include "pybind11/stl.h"

#include <utility>

#include "lsst/utils/python.h"

namespace py = pybind11;
using namespace pybind11::literals;

namespace lsst {
namespace utils {
namespace python {

PYBIND11_MODULE(_cppIndex, mod) {
    // wrap cppIndex in order to make it easy to test
    mod.def("cppIndex", (std::size_t(*)(std::ptrdiff_t, std::ptrdiff_t))cppIndex, "size"_a, "i"_a);
    mod.def("cppIndex", (std::pair<std::size_t, std::size_t>(*)(std::ptrdiff_t, std::ptrdiff_t,
                                                                std::ptrdiff_t, std::ptrdiff_t))cppIndex,
            "size_i"_a, "size_j"_a, "i"_a, "j"_a);
}

}  // python
}  // utils
}  // lsst
