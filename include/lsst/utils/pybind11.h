// -*- lsst-c++ -*-
/*
 * LSST Data Management System
 * See COPYRIGHT file at the top of the source tree.
 *
 * This product includes software developed by the
 * LSST Project (http://www.lsst.org/).
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
 * You should have received a copy of the LSST License Statement and
 * the GNU General Public License along with this program.  If not,
 * see <http://www.lsstcorp.org/LegalNotices/>.
 */

#ifndef LSST_UTILS_PYBIND11_H
#define LSST_UTILS_PYBIND11_H

#include <cstddef>
#include <memory>
#include <string>
#include <sstream>

#include <pybind11/pybind11.h>

#include "lsst/pex/exceptions.h"

namespace py = pybind11;

namespace lsst {
namespace utils {

/**
Add `__eq__` and `__ne__` methods based on two std::shared_ptr<T> pointing to the same address
*/
template<typename T, typename PyClass>
inline void addSharedPtrEquality(PyClass & cls) {
    cls.def("__eq__",
            [](std::shared_ptr<T> self, std::shared_ptr<T> other) { return self.get() == other.get(); },
            py::is_operator());
    cls.def("__ne__",
            [](std::shared_ptr<T> self, std::shared_ptr<T> other) { return self.get() != other.get(); },
            py::is_operator());
}

/**
Compute a C++ index from a Python index (negative values count from the end) and range-check.
*/
template<typename Sequence>
inline std::size_t cppIndex(Sequence const & seq, std::ptrdiff_t i) {
    auto const i_orig = i;
    auto const size = seq.size();
    if (i < 0) {
        // index backwards from the end
        i += size;
    }
    if (i < 0 || static_cast<std::size_t>(i) >= size) {
        std::ostringstream os;
        os << "Index " << i_orig << " out of range; sequence has " << size << " elements";
        throw LSST_EXCEPT(lsst::pex::exceptions::InvalidParameterError, os.str());
    }
    return static_cast<std::size_t>(i);
}

}}  // namespace lsst::utils

#endif

