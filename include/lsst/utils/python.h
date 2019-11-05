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
#include <list>
#include <functional>

#include <iostream>

#include "lsst/pex/exceptions.h"
#include "lsst/pex/exceptions/python/Exception.h"

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
 * Add `__str__` or `__repr__` method implemented by `operator<<`.
 *
 * For flexibility, this method can be used to define one or both of
 * `__str__` and `__repr__`. It can also be used to define any Python method
 * that takes no arguments and returns a string, regardless of name.
 *
 * @tparam PyClass The pybind11 class_ type. The wrapped class must
 *                 support << as a stream output operator.
 *
 * @param cls The `PyClass` object to which to add a wrapper.
 * @param method The name of the method to implement. Should be `"__str__"` or
 *               `"__repr__"`.
 */
template <class PyClass>
void addOutputOp(PyClass &cls, std::string const &method) {
    cls.def(method.c_str(), [](typename PyClass::type const &self) {
        std::ostringstream os;
        os << self;
        return os.str();
    });
}

/**
 * Add `__hash__` method implemented by `std::hash`.
 *
 * @tparam PyClass The pybind11 class_ type. The wrapped class must
 *                 have an enabled specialization of `std::hash`.
 *
 * @param cls The `PyClass` object to which to add a wrapper.
 */
template <class PyClass>
void addHash(PyClass &cls) {
    using Class = typename PyClass::type;
    cls.def("__hash__", [](Class const &self) {
        static auto const hash = std::hash<Class>();
        return hash(self);
    });
}

/**
Compute a C++ index from a Python index (negative values count from the end) and range-check.

@param[in] size  Number of elements in the collection.
@param[in] i  Index into the collection; negative values count from the end
@return index in the range [0, size - 1]

@note the size argument has type std::ptrdiff_t instead of std::size_t
in order to to match the allowed range for the i argument.

@throw Python IndexError if i not in range [-size, size - 1]
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
        throw pybind11::index_error(os.str());
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

@throw Python IndexError if either input index not in range [-size, size - 1]
*/
inline std::pair<std::size_t, std::size_t> cppIndex(std::ptrdiff_t size_i, std::ptrdiff_t size_j,
                                                    std::ptrdiff_t i, std::ptrdiff_t j) {
    try {
        return {cppIndex(size_i, i), cppIndex(size_j, j)};
    } catch (lsst::pex::exceptions::OutOfRangeError const&) {
        std::ostringstream os;
        os << "Index (" << i << ", " << j << ") not in range ["
           << -size_i << ", " << size_i - 1 << "], ["
           << -size_j << ", " << size_j - 1 << "]";
        throw pybind11::index_error(os.str());
    }
}

/**
 * A helper class for subdividing pybind11 module across multiple translation
 * units (i.e. source files).
 *
 * Merging wrappers for different classes into a single compiled module can
 * dramatically decrease the total size of the binary, but putting the source
 * for multiple wrappers into a single file slows down incremental rebuilds
 * and makes editing unwieldy.  The right approach is to define wrappers in
 * different source files and link them into a single module at build time.
 * In simple cases, that's quite straightforward: pybind11 declarations are
 * just regular C++ statements, and you can factor them out into different
 * functions in different source files.
 *
 * That approach doesn't work so well when the classes being wrapped are
 * interdependent, because bindings are only guaranteed to work when all types
 * used in a wrapped method signature have been declared to pybind11 before
 * the method using them is itself declared.  Naively, then, each source file
 * would thus have to have multiple wrapper-declaring functions, so all
 * type-wrapping functions could be executed before any method-wrapping
 * functions.  Of course, each type-wrapping function would also have to pass
 * its type object to at least one method-wrapping function (to wrap the types
 * own methods), and the result is a tangled mess of wrapper-declaring
 * functions that obfuscate the code with a lot of boilerplate.
 *
 * WrapperCollection provides a way out of that by allowing type wrappers and
 * their associated methods to be declared at a single point, but the method
 * wrappers wrapped in a lambda to defer their execution.  A single
 * WrapperCollection instance is typically constructed at the beginning of
 * a PYBIND11_MODULE block, then passed by reference to wrapper-declaring
 * functions defined in other source files.  As type and method wrappers are
 * added to the WrapperCollection by those functions, the types are registered
 * immediately, and the method-wrapping lambdas are collected.  After all
 * wrapper-declaring functions have been called, finish() is called at the
 * end of the PYBIND11_MODULE block to execute the collecting method-wrapping
 * lambdas.
 *
 * Typical usage:
 * @code
 * // _mypackage.cc
 *
 * void wrapClassA(WrapperCollection & wrappers);
 * void wrapClassB(WrapperCollection & wrappers);
 *
 * PYBIND11_MODULE(_mypackage, module) {
 *     WrapperCollection wrappers(module, "mypackage");
 *     wrapClassA(wrappers);
 *     wrapClassB(wrappers);
 *     wrappers.finish();
 * }
 * @endcode
 * @code
 * // _ClassA.cc
 *
 * void wrapClassA(WrapperCollection & wrappers) {
 *     wrappers.wrapType(
 *         py::class_<ClassA>(wrappers.module, "ClassA"),
 *         [](auto & mod, auto & cls) {
 *             cls.def("methodOnClassA", &methodOnClassA);
 *         }
 *     );
 * }
 * @endcode
 * @code
 * // _ClassB.cc
 *
 * void wrapClassB(WrapperCollection & wrappers) {
 *     wrappers.wrapType(
 *         py::class_<ClassB>(wrappers.module, "ClassB"),
 *         [](auto & mod, auto & cls) {
 *             cls.def("methodOnClassB", &methodOnClassB);
 *             mod.def("freeFunction", &freeFunction);
 *         }
 *     );
 * }
 * @endcode
 *
 * Note that we recommend the use of universal lambdas (i.e. `auto &`
 * parameters) to reduce verbosity.
 */
class LSST_PRIVATE WrapperCollection final {
    // LSST_PRIVATE above: don't export symbols used only in pybind11 wrappers
public:

    /// Function handle type used to hold deferred wrapper declaration functions.
    using WrapperCallback = std::function<void(pybind11::module &)>;

    /**
     * Construct a new WrapperCollection.
     *
     * A WrapperCollection should be constructed at or near the top of a
     * `PYBIND11_MODULE` block.
     *
     * @param[in]  module_ Module instance passed to the PYBIND11_MODULE macro.
     * @param[in]  package String name of the package all wrapped classes
     *                     should appear to be from (by resetting their
     *                     `__module__` attribute).  Note that this can lead
     *                     to problems if classes are not also lifted into
     *                     the package namespace in its `__init__.py` (in
     *                     addition to confusing users, this will prevent
     *                     unpickling from working).
     */
    explicit WrapperCollection(pybind11::module module_, std::string const & package) :
        module(module_),
        _package(package)
    {}

    // WrapperCollection is move-contructable.
    WrapperCollection(WrapperCollection && other) noexcept :
        module(std::move(other.module)),
        _package(std::move(other._package)),
        _dependencies(std::move(other._dependencies)),
        _definitions(std::move(other._definitions))
    {}

    // WrapperCollection is not copyable or assignable.
    WrapperCollection(WrapperCollection const &) = delete;
    WrapperCollection & operator=(WrapperCollection const &) = delete;
    WrapperCollection & operator=(WrapperCollection &&) = delete;

    ~WrapperCollection() noexcept {
        if (!std::uncaught_exception() && !_definitions.empty()) {
            PyErr_SetString(PyExc_ImportError,
                            "WrapperCollection::finish() not called; module definition incomplete.");
            PyErr_WriteUnraisable(module.ptr());
        }
    }

    /**
     * Create a WrapperCollection for a submodule defined in the same binary.
     *
     * WrapperCollections created with makeSubmodule should generally be
     * destroyed by moving them into a call to collectSubmodule; this will
     * cause all deferred definitions to be executed when the parent
     * WrapperCollection's finish() method is called.
     *
     * @param  name  Relative name of the submodule.
     *
     * Attributes added to the returned WrapperCollection will actually be put
     * in a submodule that adds an underscore prefix to ``name``, with
     * ``__module__`` set with the expectation that they will be lifted
     * into a package without that leading underscore by a line in
     * ``__init__.py`` like:
     *
     *     from ._package import _submodule as submodule
     *
     * This is necessary to make importing ``_package`` possible when
     * ``submodule`` already exists as a normal (i.e. directory-based) package.
     * Of course, in that case, you'd instead use a ``submodule/__init__.py``
     * with a line like:
     *
     *     from .._package._submodule import *
     *
     * @return a new WrapperCollection instance that sets the `__module__`
     *         of any classes added to it to `{package}.{name}`.
     */
    WrapperCollection makeSubmodule(std::string const & name) {
        return WrapperCollection(module.def_submodule(("_" + name).c_str()), _package + "." + name);
    }

    /**
     * Merge deferred definitions in the given submodule into the parent
     * WrapperCollection.
     *
     * @param submodule  A WrapperCollection created by makeSubmodule.
     *                   Will be consumed (and must be an rvalue).
     */
    void collectSubmodule(WrapperCollection && submodule) {
        _dependencies.splice(_dependencies.end(), submodule._dependencies);
        _definitions.splice(_definitions.end(), submodule._definitions);
    }

    /**
     * Indicate an external module that provides a base class for a subsequent
     * addType call.
     *
     * Dependencies that provide base classes cannot be deferred until after
     * types are declared, and are always imported immediately.
     *
     * @param[in] name  Name of the module to import (absolute).
     */
    void addInheritanceDependency(std::string const & name) {
        pybind11::module::import(name.c_str());
    }

    /**
     * Indicate an external module that provides a type used in function/method
     * signatures.
     *
     * Dependencies that provide classes are imported after types in the
     * current module are declared and before any methods and free functions
     * in the current module are declared.
     *
     * @param[in] name  Name of the module to import (absolute).
     */
    void addSignatureDependency(std::string const & name) {
        _dependencies.push_back(name);
    }

    /**
     * Add a set of wrappers without defining a class.
     *
     * @param[in] function A callable object that takes a single
     *                     `pybind11::module` argument (by reference) and
     *                     adds pybind11 wrappers to it, to be called later
     *                     by `finish()`.
     */
    void wrap(WrapperCallback function) {
        _definitions.emplace_back(std::make_pair(module, function));
    }

    /**
     * Add a type (class or enum) wrapper, deferring method and other
     * attribute definitions until finish() is called.
     *
     * @param[in] cls       A `pybind11::class_` or `enum_` instance.
     * @param[in] function  A callable object that takes a `pybind11::module`
     *                      argument and a `pybind11::class_` (or `enum_`)
     *                      argument (both by reference) and defines wrappers
     *                      for the class's methods and other attributes.
     *                      Will be called with `this->module` and `cls` by
     *                      `finish()`.
     * @param[in] setModuleName  If true (default), set `cls.__module__` to
     *                           the package string this `WrapperCollection`
     *                           was initialized with.
     *
     * @return the `cls` argument for convenience
     */
    template <typename PyType, typename ClassWrapperCallback>
    PyType wrapType(PyType cls, ClassWrapperCallback function, bool setModuleName=true) {
        if (setModuleName) {
            cls.attr("__module__") = _package;
        }
        // lambda below is mutable so it can modify the captured `cls` variable
        wrap(
            [cls=cls, function=std::move(function)] (pybind11::module & mod) mutable -> void {
                function(mod, cls);
            }
        );
        return cls;
    }

    /**
     * Wrap a C++ exception as a Python exception.
     *
     * @tparam  CxxException  C++ Exception type to wrap.
     * @tparam  CxxBase       Base class of CxxException.
     *
     * @param[in] pyName   Python name of the new exception.
     * @param[in] pyBase   Python name of the pex::exceptions Exception type
     *                     the new exception inherits from.
     * @param[in] setModuleName  If true (default), set `cls.__module__` to
     *                           the package string this `WrapperCollection`
     *                           was initialized with.
     *
     * @return a `pybind11::class_` instance (template parameters unspecified)
     *         representing the Python type of the new exception.
     */
    template <typename CxxException, typename CxxBase>
    auto wrapException(std::string const & pyName, std::string const & pyBase, bool setModuleName=true) {
        auto cls = pex::exceptions::python::declareException<CxxException, CxxBase>(module, pyName, pyBase);
        if (setModuleName) {
            cls.attr("__module__") = _package;
        }
        return cls;
    }

    /**
     * Invoke all deferred wrapper-declaring callables.
     *
     * `finish()` should be called exactly once, at or near the end of a
     * `PYBIND11_MODULE` block.
     */
    void finish() {
        for (auto dep = _dependencies.begin(); dep != _dependencies.end(); dep = _dependencies.erase(dep)) {
            pybind11::module::import(dep->c_str());
        }
        for (auto def = _definitions.begin(); def != _definitions.end(); def = _definitions.erase(def)) {
            (def->second)(def->first);  // WrapperCallback(module)
        }
    }

    /**
     * The module object passed to the `PYBIND11_MODULE` block that contains
     * this WrapperCollection.
     */
    pybind11::module module;

private:
    std::string _package;
    std::list<std::string> _dependencies;
    std::list<std::pair<pybind11::module, WrapperCallback>> _definitions;
};


}}}  // namespace lsst::utils::python

#endif
