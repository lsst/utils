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

#ifndef LSST_UTILS_PYTHON_PYSHAREDPTR_H
#define LSST_UTILS_PYTHON_PYSHAREDPTR_H

#include "pybind11/pybind11.h"

#include <memory>

namespace lsst {
namespace utils {
namespace python {

/* Workaround for C++ objects outliving Python objects
 * by Xfel and florianwechsung, https://github.com/pybind/pybind11/issues/1389
 */
/**
 * A shared pointer that tracks both a C++ object and its associated PyObject.
 *
 * Each group of PySharedPtr for a given object collectively counts as one
 * reference to that object for the purpose of Python garbage collection.
 *
 * A PySharedPtr is implicitly convertible to and from a std::shared_ptr to
 * minimize API impact. Any `shared_ptr` created this way will (I think) keep
 * the Python reference alive, as described above.
 */
template <typename T>
class PySharedPtr final {
public:
    using element_type = T;

    /**
     * Create a pointer that counts as an extra reference in the
     * Python environment.
     *
     * @param ptr a pointer to a pybind11-managed object.
     */
    explicit PySharedPtr(T* const ptr) : _impl() {
        if (ptr != nullptr) {
            // `cast` returns new PyObject only if `*ptr` not yet associated with one
            PyObject* pyObj = pybind11::cast(ptr).ptr();
            Py_INCREF(pyObj);
            // if any operation with shared_ptr fails, pyObj will get decremented correctly
            std::shared_ptr<PyObject> manager(pyObj, [](PyObject* const obj) noexcept {
                if (obj != nullptr) Py_DECREF(obj);
            });
            _impl = std::shared_ptr<T>(manager, ptr);
        }
    }

    PySharedPtr(PySharedPtr const&) noexcept = default;
    PySharedPtr(PySharedPtr&&) noexcept = default;
    PySharedPtr& operator=(PySharedPtr const&) noexcept = default;
    PySharedPtr& operator=(PySharedPtr&&) noexcept = default;
    ~PySharedPtr() noexcept = default;

    PySharedPtr(std::shared_ptr<T> r) noexcept : _impl(std::move(r)) {}
    operator std::shared_ptr<T>() noexcept { return _impl; }

    T* get() const noexcept { return _impl.get(); }

private:
    std::shared_ptr<T> _impl;
};

}  // namespace python
}  // namespace utils
}  // namespace lsst

// Macro must be called in the global namespace
PYBIND11_DECLARE_HOLDER_TYPE(T, lsst::utils::python::PySharedPtr<T>);

#endif
