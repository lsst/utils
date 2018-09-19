/* 
 * LSST Data Management System
 * Copyright 2008-2016  AURA/LSST.
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
 * see <https://www.lsstcorp.org/LegalNotices/>.
 */

#include <limits>
#include <sstream>

#include "pybind11/pybind11.h"
#include "pybind11/operators.h"
#include "pybind11/numpy.h"

#include "lsst/utils/python.h"

namespace py = pybind11;

class Example {
public:

    explicit Example(std::string const & v) : _value(v) {}

    explicit Example(bool b) : _value("boolean") {}

    Example(Example const & other) : _value(other._value) {}

    Example & get1() { return *this; }
    Example & get2() { return *this; }
    Example & get3() { return *this; }

    std::string getValue() const { return _value; }
    void setValue(std::string const & v) { _value = v; }

    bool operator==(Example const & other) const {
        return other._value == _value;
    }
    bool operator!=(Example const & other) const {
        return !(*this == other);
    }

private:
    std::string _value;
};

inline std::ostream & operator<<(std::ostream & os, Example const & ex) {
    return os << "Example(" << ex.getValue() << ")";
}

template <typename T>
T acceptNumber(T value) { return value; }

template <typename T>
T acceptNumberConstRef(T const & value) { return value; }

// This is a dummy overload that's intended never to actually succeed - we just want to make
// sure the typecheck typemaps work, and we need it to be templated just so we get one for
// each instantiated wrapper for the other acceptNumber, and numeric_limits is something
// templated we know we won't be passing.
template <typename T>
bool acceptNumber(std::numeric_limits<T> *) { return false; }

template <typename T>
bool acceptNumberConstRef(std::numeric_limits<T> *) { return false; }

std::string getName(int) { return "int"; }
std::string getName(double) { return "double"; }

void wrapExample(lsst::utils::python::WrapperCollection & wrappers) {
    wrappers.wrapType(
        py::class_<Example>(wrappers.module, "Example"),
        [](auto & mod, auto & cls) {
            cls.def(py::init<std::string const &>());
            cls.def(py::init<bool>());
            cls.def(py::init<Example const &>());

            cls.def("get1", &Example::get1);
            cls.def("get2", &Example::get1);
            cls.def("get3", &Example::get1);

            cls.def("getValue", &Example::getValue);
            cls.def("setValue", &Example::setValue);

            cls.def(py::self == py::self);
            cls.def(py::self != py::self);

            lsst::utils::python::addOutputOp(cls, "__str__");
            lsst::utils::python::addOutputOp(cls, "__repr__");
        }
    );
}

PYBIND11_MODULE(_example, mod) {
    lsst::utils::python::WrapperCollection wrappers(mod, "example");
    wrapExample(wrappers);
    wrappers.wrapFunctions(
        [](auto & mod) {
            mod.def("accept_float32", [](float val){return acceptNumber(val);});
            mod.def("accept_float64", [](double val){return acceptNumber(val);});
            mod.def("accept_uint8", [](unsigned char val){return acceptNumber(val);});
            mod.def("accept_uint16", [](unsigned short val){return acceptNumber(val);});
            mod.def("accept_uint32", [](unsigned int val){return acceptNumber(val);});
            mod.def("accept_uint64", [](unsigned long long val){return acceptNumber(val);});
            mod.def("accept_int8", [](signed char val){return acceptNumber(val);});
            mod.def("accept_int16", [](short val){return acceptNumber(val);});
            mod.def("accept_int32", [](int val){return acceptNumber(val);});
            mod.def("accept_int64", [](long long val){return acceptNumber(val);});

            mod.def("accept_cref_float32", [](float const &val){return acceptNumber(val);});
            mod.def("accept_cref_float64", [](double const &val){return acceptNumber(val);});
            mod.def("accept_cref_uint8", [](unsigned char const &val){return acceptNumber(val);});
            mod.def("accept_cref_uint16", [](unsigned short const &val){return acceptNumber(val);});
            mod.def("accept_cref_uint32", [](unsigned int const &val){return acceptNumber(val);});
            mod.def("accept_cref_uint64", [](unsigned long long const &val){return acceptNumber(val);});
            mod.def("accept_cref_int8", [](signed char const &val){return acceptNumber(val);});
            mod.def("accept_cref_int16", [](short const &val){return acceptNumber(val);});
            mod.def("accept_cref_int32", [](int const &val){return acceptNumber(val);});
            mod.def("accept_cref_int64", [](long long const &val){return acceptNumber(val);});

            mod.def("getName", (std::string (*)(int)) getName);
            mod.def("getName", (std::string (*)(double)) getName);
        }
    );
    wrappers.finish();
}
