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

#ifndef LSST_UTILS_PYTHON_TEMPLATEINVOKER_H
#define LSST_UTILS_PYTHON_TEMPLATEINVOKER_H

#include "pybind11/pybind11.h"
#include "pybind11/numpy.h"

#include <iostream>

namespace lsst { namespace utils { namespace python {

/**
 * A helper class for wrapping C++ template functions as Python functions with dtype arguments.
 *
 * TemplateInvoker takes a templated callable object, a `pybind11::dtype`
 * object, and a sequence of supported C++ types via its nested `Tag` struct.
 * The callable is invoked with a scalar argument of the type matching the
 * `dtype` object.  If none of the supported C++ types match, a different
 * error callback is invoked instead.
 *
 * As an example, we'll wrap this function:
 * @code
 * template <typename T>
 * T doSomething(std::string const & argument);
 * @endcode
 *
 * TemplateInvoker provides a default error callback, which we'll use here
 * (otherwise you'd need to pass one when constructing the TemplateInvoker).
 *
 * For the main callback, we'll define this helper struct:
 * @code
 * struct DoSomethingHelper {
 *
 *     template <typename T>
 *     T operator()(T) const {
 *         return doSomething<T>(argument);
 *     }
 *
 *     std::string argument;
 * };
 * @endcode
 *
 * The pybind11 wrapper for `doSomething` is then another lambda that uses
 * `TemplateInvoker::apply` to call the helper:
 * @code
 * mod.def(
 *     "doSomething",
 *     [](std::string const & argument, py::dtype const & dtype) {
 *         return TemplateInvoker().apply(
 *             DoSomethingHelper{argument},
 *             dtype,
 *             TemplateInvoker::Tag<int, float, double>()
 *         );
 *     },
 *     "argument"_a
 * );
 * @endcode
 *
 * The type returned by the helper callable's `operator()` can be anything
 * pybind11 knows how to convert to Python.
 *
 * While defining a full struct with a templated `operator()` makes it more
 * obvious what TemplateInvoker is doing, it's much more concise to use a
 * universal lambda with the `decltype` operator. This wrapper is equivalent
 * to the one above, but it doesn't need `DoSomethingHelper`:
 * @code
 * mod.def(
 *     "doSomething",
 *     [](std::string const & argument, py::dtype const & dtype) {
 *         return TemplateInvoker().apply(
 *             [&argument](auto t) { return doSomething<decltype(t)>(argument); },
 *             dtype,
 *             TemplateInvoker::Tag<int, float, double>()
 *         );
 *     },
 *     "argument"_a
 * );
 * @endcode
 * Note that the value of `t` here doesn't matter; what's important is that its
 * C++ type corresponds to the type passed in the `dtype` argument.  So instead
 * of using that value, we use the `decltype` operator to extract that type and
 * use it as a template parameter.
 */
class TemplateInvoker {
public:

    /// A simple tag type used to pass one or more types as a function argument.
    template <typename ...Types>
    struct Tag {};

    /// Callback type for handling unmatched-type errors.
    using OnErrorCallback = std::function<pybind11::object(pybind11::dtype const & dtype)>;

    /// Callback used for handling unmatched-type errors by default.
    static pybind11::object handleErrorDefault(pybind11::dtype const & dtype) {
        PyErr_Format(PyExc_TypeError, "dtype '%R' not supported.", dtype.ptr());
        throw pybind11::error_already_set();
    }

    /**
     * Construct a TemplateInvoker that calls the given object when no match is found.
     *
     * The callback should have the same signature as handleErrorDefault; the
     * dtype actually passed from Python is passed so it can be included in
     * error messages.
     */
    explicit TemplateInvoker(OnErrorCallback onError) : _onError(std::move(onError)) {}

    /// Construct a TemplateInvoker that calls handleErrorDefault when no match is found.
    TemplateInvoker() : TemplateInvoker(handleErrorDefault) {}

    /**
     * Call and return `function(static_cast<T>(0))` with the type T that
     * matches a given NumPy `dtype` object.
     *
     * @param[in]  function     Callable object to invoke.  Must have an
     *                          overloaded operator() that takes any `T` in
     *                          the sequence `TypesToTry`, and a
     *                          `fail(py::dtype)` method to handle the case
    *                          where none of the given types match.
     *
     * @param[in]  dtype        NumPy dtype object indicating the template
     *                          specialization to invoke.
     *
     * @param[in]  typesToTry   A `Tag` instance parameterized with the list of
     *                          types to try to match to `dtype`.
     *
     * @return the result of calling `function` with the matching type, after
     *         converting it into a Python object.
     *
     * @exceptsafe the same as the exception safety of `function`
     */
    template <typename Function, typename ...TypesToTry>
    pybind11::object apply(
        Function function,
        pybind11::dtype const & dtype,
        Tag<TypesToTry...> typesToTry
    ) const {
        return _apply(function, dtype, typesToTry);
    }

private:

    template <typename Function>
    pybind11::object _apply(Function & function, pybind11::dtype const & dtype, Tag<>) const {
        return _onError(dtype);
    }

    template <typename Function, typename T, typename ...A>
    pybind11::object _apply(Function & function, pybind11::dtype const & dtype, Tag<T, A...>) const {
        if (pybind11::detail::npy_api::get().PyArray_EquivTypes_(dtype.ptr(),
                                                                 pybind11::dtype::of<T>().ptr())) {
            return pybind11::cast(function(static_cast<T>(0)));
        }
        return _apply(function, dtype, Tag<A...>());
    }

    OnErrorCallback _onError;
};

}}}  // namespace lsst::utils::python

#endif
