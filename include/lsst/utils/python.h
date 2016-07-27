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

#ifndef LSST_UTILS_PYTHON_H
#define LSST_UTILS_PYTHON_H

#include "pybind11/pybind11.h"

#include <cstddef>
#include <memory>
#include <string>
#include <sstream>
#include <utility>

#include "lsst/pex/exceptions.h"

namespace lsst {
namespace utils {
namespace python {

/**
Add `__eq__` and `__ne__` methods based on two std::shared_ptr<T> pointing to the same address

@tparam T  The type to which the std::shared_ptr points.
@tparam PyClass  The pybind11 class_ type; this can be automatically deduced.

Example:

lsst::afw::table records are considered equal if two `std::shared_ptr<record>` point to the same record.
This is wrapped as follows for `lsst::afw::table::BaseRecord`, where `cls` is an instance of
`pybind11::class_<BaseRecord, std::shared_ptr<BaseRecord>>)`:

    utils::addSharedPtrEquality<BaseRecord>(cls);

Note that all record subclasses inherit this behavior without needing to call this function.
*/
template<typename T, typename PyClass>
inline void addSharedPtrEquality(PyClass & cls) {
    cls.def("__eq__",
            [](std::shared_ptr<T> self, std::shared_ptr<T> other) { return self.get() == other.get(); },
            pybind11::is_operator());
    cls.def("__ne__",
            [](std::shared_ptr<T> self, std::shared_ptr<T> other) { return self.get() != other.get(); },
            pybind11::is_operator());
}

/**
Compute a C++ index from a Python index (negative values count from the end) and range-check.

@param[in] size  Number of elements in the collection.
@param[in] i  Index into the collection; negative values count from the end
@return index in the range [0, size - 1]

@throw lsst::pex::exceptions::OutOfRangeError if i not in range [-size, size - 1]
*/
inline std::size_t cppIndex(std::ptrdiff_t size, std::ptrdiff_t i) {
    auto const i_orig = i;
    if (i < 0) {
        // index backwards from the end
        i += size;
    }
    if (i < 0 || i >= size) {
        std::ostringstream os;
        os << "Index " << i_orig << " not in range [" << -size << ", " << size - 1 << "]";
        throw LSST_EXCEPT(lsst::pex::exceptions::OutOfRangeError, os.str());
    }
    return static_cast<std::size_t>(i);
}

/**
Compute a pair of C++ indices from a pair of Python indices (negative values count from the end)
and range-check.

@param[in] size_i  Number of elements along the first axis.
@param[in] size_j  Number of elements along the second axis.
@param[in] i  Index along first axis; negative values count from the end
@param[in] j  Index along second axis; negative values count from the end
@return a std::pair of indices, each in the range [0, size - 1]

@throw lsst::pex::exceptions::OutOfRangeError if either input index not in range [-size, size - 1]
*/
inline std::pair<std::size_t, std::size_t> cppIndex(std::ptrdiff_t size_i, std::ptrdiff_t size_j,
                                                    std::ptrdiff_t i, std::ptrdiff_t j) {
    try {
        return {cppIndex(size_i, i), cppIndex(size_j, j)};
    } catch (lsst::pex::exceptions::OutOfRangeError) {
        std::ostringstream os;
        os << "Index (" << i << ", " << j << ") not in range ["
           << -size_i << ", " << size_i - 1 << "], ["
           << -size_j << ", " << size_j - 1 << "]";
        throw LSST_EXCEPT(lsst::pex::exceptions::OutOfRangeError, os.str());
    }
}

}}}  // namespace lsst::utils::python

#endif

