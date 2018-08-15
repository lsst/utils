#ifndef LSST_UTILS_PYTHON_CACHE_H
#define LSST_UTILS_PYTHON_CACHE_H

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
