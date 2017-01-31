// -*- lsst-c++ -*-
/*
 * LSST Data Management System
 * Copyright 2015 LSST/AURA
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
%{
#include <cstdint>
#include <climits>
%}

%define %declareFloatingTypemap(CTYPE, PRECEDENCE)
    %typemap(typecheck, precedence=SWIG_TYPECHECK_##PRECEDENCE, noblock=1)
        CTYPE, CTYPE const, CTYPE const &, CTYPE const *
    %{
        $1 = (PyFloat_Check($input) || PyInt_Check($input) || PyLong_Check($input)
#ifdef PY_ARRAY_UNIQUE_SYMBOL
              || PyArray_IsScalar($input, Floating) || PyArray_IsScalar($input, Integer)
#endif
        ) ? 1 : 0;
    %}
    %typemap(in) CTYPE (PyObject * descr), CTYPE const (PyObject * descr)
        %{
        if (PyFloat_Check($input)) {
            $1 = static_cast<CTYPE>(PyFloat_AsDouble($input));
#ifdef PY_ARRAY_UNIQUE_SYMBOL
        } else if (PyArray_IsScalar($input, Floating) || PyArray_IsScalar($input, Integer)) {
            descr = reinterpret_cast<PyObject*>(PyArray_DescrNewFromType(NPY_##PRECEDENCE));
            PyArray_CastScalarToCtype($input, reinterpret_cast<void*>(&$1),
                                      reinterpret_cast<PyArray_Descr*>(descr));
            Py_XDECREF(descr);
#else
            (void)descr; // prevent unused variable warnings
#endif
        } else if (PyInt_Check($input)) {
            $1 = static_cast<CTYPE>(PyInt_AsLong($input));
        } else if (PyLong_Check($input)) {
            $1 = static_cast<CTYPE>(PyLong_AsUnsignedLongLong($input));
        } else {
            PyErr_SetString(PyExc_TypeError, "Cannot convert value to " #CTYPE);
            return NULL;
        }
        if (PyErr_Occurred()) {
            return NULL;
        }
    %}
    // We have to duplicate the by-value in typemap for const reference and pointer, and modify it slightly
    // because for these $1 is a pointer.
    %typemap(in)
        CTYPE const & (PyObject * descr, CTYPE tmp),
        CTYPE const * (PyObject * descr, CTYPE tmp)
    %{
        if (PyFloat_Check($input)) {
            tmp = static_cast<CTYPE>(PyFloat_AsDouble($input));
        } else if (PyInt_Check($input)) {
            tmp = static_cast<CTYPE>(PyInt_AsLong($input));
        } else if (PyLong_Check($input)) {
            tmp = static_cast<CTYPE>(PyLong_AsUnsignedLongLong($input));
#ifdef PY_ARRAY_UNIQUE_SYMBOL
        } else if (PyArray_IsScalar($input, Floating) || PyArray_IsScalar($input, Integer)) {
            descr = reinterpret_cast<PyObject*>(PyArray_DescrNewFromType(NPY_##PRECEDENCE));
            PyArray_CastScalarToCtype($input, reinterpret_cast<void*>(&tmp),
                                      reinterpret_cast<PyArray_Descr*>(descr));
            Py_XDECREF(descr);
#else
            (void)descr; // prevent unused variable warnings
#endif
        } else {
            PyErr_SetString(PyExc_TypeError, "Cannot convert value to " #CTYPE);
            return NULL;
        }
        if (PyErr_Occurred()) {
            return NULL;
        }
        $1 = &tmp;
    %}
%enddef

%define %declareUnsignedTypemap(CTYPE, PRECEDENCE)
    %typemap(typecheck, precedence=SWIG_TYPECHECK_##PRECEDENCE, noblock=1)
        CTYPE, CTYPE const, CTYPE const &, CTYPE const *
    %{
        $1 = (PyInt_Check($input) || PyLong_Check($input)
#ifdef PY_ARRAY_UNIQUE_SYMBOL
              || PyArray_IsScalar($input, Integer)
#endif
        ) ? 1 : 0;
    %}
    %typemap(in) CTYPE (PyObject * descr, std::uint64_t tmp, PyObject * zero),
                 CTYPE const (PyObject * descr, std::uint64_t tmp, PyObject * zero) %{
        if (PyInt_Check($input)) {
            tmp = PyInt_AsLong($input);
        } else if (PyLong_Check($input)) {
            tmp = PyLong_AsUnsignedLongLong($input);
#ifdef PY_ARRAY_UNIQUE_SYMBOL
        } else if (PyArray_IsScalar($input, Integer)) {
            descr = reinterpret_cast<PyObject*>(PyArray_DescrNewFromType(NPY_UINT64));
            PyArray_CastScalarToCtype($input, reinterpret_cast<void*>(&tmp),
                                      reinterpret_cast<PyArray_Descr*>(descr));
            Py_XDECREF(descr);
#else
            (void)descr; // prevent unused variable warnings
#endif
        } else {
            PyErr_SetString(PyExc_TypeError, "Cannot convert value to " #CTYPE);
            return NULL;
        }
        if (PyErr_Occurred()) {
            return NULL;
        }
        $1 = tmp;
        zero = PyInt_FromLong(0);
        if (PyObject_RichCompareBool($input, zero, Py_GT) && static_cast<std::uint64_t>($1) != tmp) {
            Py_XDECREF(zero);
            PyErr_SetString(PyExc_OverflowError, "Overflow error converting to " #CTYPE);
            return NULL;
        }
        Py_XDECREF(zero);
    %}
    // We have to duplicate the by-value in typemap for const reference and pointer, and modify it slightly
    // because for these $1 is a pointer.
    %typemap(in) CTYPE const & (PyObject * descr, std::uint64_t tmp1, CTYPE tmp2, PyObject * zero),
                 CTYPE const * (PyObject * descr, std::uint64_t tmp1, CTYPE tmp2, PyObject * zero)
    %{
        if (PyInt_Check($input)) {
            tmp1 = PyInt_AsLong($input);
        } else if (PyLong_Check($input)) {
            tmp1 = PyLong_AsUnsignedLongLong($input);
#ifdef PY_ARRAY_UNIQUE_SYMBOL
        } else if (PyArray_IsScalar($input, Integer)) {
            descr = reinterpret_cast<PyObject*>(PyArray_DescrNewFromType(NPY_UINT64));
            PyArray_CastScalarToCtype($input, reinterpret_cast<void*>(&tmp1),
                                      reinterpret_cast<PyArray_Descr*>(descr));
            Py_XDECREF(descr);
#else
            (void)descr; // prevent unused variable warnings
#endif
        } else {
            PyErr_SetString(PyExc_TypeError, "Cannot convert value to " #CTYPE);
            return NULL;
        }
        if (PyErr_Occurred()) {
            return NULL;
        }
        tmp2 = tmp1;
        zero = PyInt_FromLong(0);
        if (PyObject_RichCompareBool($input, zero, Py_GT) && static_cast<std::uint64_t>(tmp2) != tmp1) {
            Py_XDECREF(zero);
            PyErr_SetString(PyExc_OverflowError, "Overflow error converting to " #CTYPE);
            return NULL;
        }
        Py_XDECREF(zero);
        $1 = &tmp2;
    %}
%enddef

%define %declareSignedTypemap(CTYPE, PRECEDENCE)
    %typemap(typecheck, precedence=SWIG_TYPECHECK_##PRECEDENCE, noblock=1)
        CTYPE, CTYPE const &, CTYPE const *
    %{
        $1 = (PyInt_Check($input) || PyLong_Check($input)
#ifdef PY_ARRAY_UNIQUE_SYMBOL
              || PyArray_IsScalar($input, Integer)
#endif
        ) ? 1 : 0;
    %}
    %typemap(in) CTYPE (PyObject * descr, std::int64_t tmp),
                 CTYPE const (PyObject * descr, std::int64_t tmp)
    %{
        if (PyInt_Check($input)) {
            tmp = PyInt_AsLong($input);
        } else if (PyLong_Check($input)) {
            tmp = PyLong_AsLongLong($input);
#ifdef PY_ARRAY_UNIQUE_SYMBOL
        } else if (PyArray_IsScalar($input, Integer)) {
            descr = reinterpret_cast<PyObject*>(PyArray_DescrNewFromType(NPY_INT64));
            PyArray_CastScalarToCtype($input, reinterpret_cast<void*>(&tmp),
                                      reinterpret_cast<PyArray_Descr*>(descr));
            Py_XDECREF(descr);
#else
            (void)descr; // prevent unused variable warnings
#endif
        } else {
            PyErr_SetString(PyExc_TypeError, "Cannot convert value to " #CTYPE);
            return NULL;
        }
        if (PyErr_Occurred()) {
            return NULL;
        }
        $1 = tmp;
        if (static_cast<std::int64_t>($1) != tmp) {
            PyErr_SetString(PyExc_OverflowError, "Overflow error converting to " #CTYPE);
            return NULL;
        }
    %}
    %typemap(in) CTYPE const & (PyObject * descr, std::int64_t tmp1, CTYPE tmp2),
                 CTYPE const * (PyObject * descr, std::int64_t tmp1, CTYPE tmp2)
    %{
        if (PyInt_Check($input)) {
            tmp1 = PyInt_AsLong($input);
        } else if (PyLong_Check($input)) {
            tmp1 = PyLong_AsLongLong($input);
#ifdef PY_ARRAY_UNIQUE_SYMBOL
        } else if (PyArray_IsScalar($input, Integer)) {
            descr = reinterpret_cast<PyObject*>(PyArray_DescrNewFromType(NPY_INT64));
            PyArray_CastScalarToCtype($input, reinterpret_cast<void*>(&tmp1),
                                      reinterpret_cast<PyArray_Descr*>(descr));
            Py_XDECREF(descr);
#endif
        } else {
            PyErr_SetString(PyExc_TypeError, "Cannot convert value to " #CTYPE);
            return NULL;
        }
        if (PyErr_Occurred()) {
            return NULL;
        }
        tmp2 = tmp1;
        if (static_cast<std::int64_t>(tmp2) != tmp1) {
            PyErr_SetString(PyExc_OverflowError, "Overflow error converting to " #CTYPE);
            return NULL;
        }
        $1 = &tmp2;
    %}
%enddef

%define %initializeNumPy(MODULE_NAME)
    %{
    #include <cstdint>
    #include <climits>
    #define PY_ARRAY_UNIQUE_SYMBOL LSST_##MODULE_NAME##_ARRAY_API
    #include "numpy/arrayobject.h"
    %}

    %init %{
        import_array();
    %}

    %declareUnsignedTypemap(unsigned char, UINT8)
    %declareSignedTypemap(signed char, INT8)

    %declareUnsignedTypemap(unsigned short, UINT16)
    %declareSignedTypemap(short, INT16)
    %declareUnsignedTypemap(unsigned int, UINT32)
    %declareSignedTypemap(int, INT32)

#if LONG_MAX == 2147483647
    %declareUnsignedTypemap(unsigned long, UINT32)
    %declareSignedTypemap(long, INT32)
#else
    %declareUnsignedTypemap(unsigned long, UINT64)
    %declareSignedTypemap(long, INT64)
#endif

    %declareUnsignedTypemap(unsigned long long, UINT64)
    %declareSignedTypemap(long long, INT64)

    %declareFloatingTypemap(float, FLOAT)
    %declareFloatingTypemap(double, DOUBLE)

%enddef // %initializeNumPy
