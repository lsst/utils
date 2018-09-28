#ifndef LSST_UTILS_PYTHON_CACHE_H
#define LSST_UTILS_PYTHON_CACHE_H
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

#include <functional>  // for std::function
#include "pybind11/pybind11.h"
#include "pybind11/stl.h"
#include "pybind11/functional.h"  // for binding std::function

#include "lsst/utils/Cache.h"

namespace py = pybind11;
using namespace pybind11::literals;

namespace lsst {
namespace utils {
namespace python {

template <typename Key, typename Value, typename KeyHash=boost::hash<Key>,
          typename KeyPred=std::equal_to<Key>>
void declareCache(py::module & mod, std::string const& name) {
    typedef lsst::utils::Cache<Key, Value, KeyHash, KeyPred> Class;
    py::class_<Class> cls(mod, name.c_str());

    cls.def(py::init<std::size_t>(), "maxElements"_a=0);
    cls.def("__call__",
            [](Class & self, Key const& key, std::function<Value(Key const& key)> func) {
                py::gil_scoped_release release;
                return self(key, func);
            }, "key"_a, "func"_a);
    cls.def("__getitem__", &Class::operator[]);
    cls.def("add", &Class::add, "key"_a, "value"_a);
    cls.def("size", &Class::size);
    cls.def("__len__", &Class::size);
    cls.def("keys", &Class::keys);
    cls.def("contains", &Class::contains);
    cls.def("__contains__", &Class::contains);
    cls.def("capacity", &Class::capacity);
    cls.def("reserve", &Class::reserve);
    cls.def("flush", &Class::flush);
}

}}} // namespace lsst::utils::python

#endif // ifndef LSST_UTILS_PYTHON_CACHE_H
