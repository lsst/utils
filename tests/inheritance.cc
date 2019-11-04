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

#include <memory>
#include <string>

#include "lsst/utils/python/PySharedPtr.h"

namespace py = pybind11;
using namespace pybind11::literals;

namespace lsst {
namespace utils {
namespace python {
/* Test framework based on example by cdyson37,
 * https://github.com/pybind/pybind11/issues/1546
 */

class CppBase {
public:
    std::string nonOverridable() const noexcept { return "42"; }
    virtual std::string overridable() const { return ""; }
    virtual std::string abstract() const = 0;
};

class CppDerived : public CppBase {
public:
    std::string overridable() const override { return "overridden"; }
    std::string abstract() const override { return "implemented"; }
};

template <class Base = CppBase>
class Trampoline : public Base {
public:
    using Base::Base;

    std::string overridable() const override { PYBIND11_OVERLOAD(std::string, Base, overridable, ); }
    std::string abstract() const override { PYBIND11_OVERLOAD_PURE(std::string, Base, abstract, ); }
};

class CppStorage final {
public:
    explicit CppStorage(std::shared_ptr<CppBase> ptr) : ptr(ptr) {}

    std::shared_ptr<CppBase> ptr;
};

std::shared_ptr<CppBase> getFromStorage(CppStorage const& holder) { return holder.ptr; }

std::string printFromCpp(CppBase const& obj) {
    return obj.nonOverridable() + " " + obj.overridable() + " " + obj.abstract();
}

PYBIND11_MODULE(_inheritance, mod) {
    py::class_<CppBase, Trampoline<>, PySharedPtr<CppBase>>(mod, "CppBase").def(py::init<>());
    py::class_<CppDerived, Trampoline<CppDerived>, CppBase, PySharedPtr<CppDerived>>(mod, "CppDerived")
            .def(py::init<>());

    py::class_<CppStorage, std::shared_ptr<CppStorage>>(mod, "CppStorage")
            .def(py::init<std::shared_ptr<CppBase>>());

    mod.def("getFromStorage", &getFromStorage, "holder"_a);
    mod.def("printFromCpp", &printFromCpp);
}

}  // namespace python
}  // namespace utils
}  // namespace lsst
