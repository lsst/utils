// -*- lsst-c++ -*-

/* 
 * LSST Data Management System
 * Copyright 2008, 2009, 2010 LSST Corporation.
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
 

// This SWIG file provides generally useful functionality, macros,
// and includes to all LSST packages.
//
// Any types or SWIG typemaps added to this file will therefore
// affect a lot of code, and should be _very_ carefully considered.


#if defined(SWIGPYTHON)

// Don't allow user to add attributes to C-defined classes; catches a variety of
// typos when the user _thinks_ that they're setting a C-level object, but in
// reality they're adding a new (and irrelevent) member to the class
%pythonnondynamic;
#endif

%naturalvar;  // use const reference typemaps

%include "cpointer.i"
%include "exception.i"
%include "stdint.i"
%include "std_list.i"
%include "std_map.i"
%include "std_string.i"
%include "std_set.i"
%include "std_vector.i"
%include "std_iostream.i"
%include "boost_shared_ptr.i"
%include "carrays.i"
%include "typemaps.i"

// N.b. these may interfere with the use of e.g. std_list.i for primitive types;
// you will have to say e.g.
// %clear int &;
//    %template(listInt)   std::list<int>;
//    %template(mapIntInt) std::map<int,int>;
// %apply int &OUTPUT { int & };

// Removed by ktl 2007-11-06 due to interference with other code.
// No methods visible to Python are expected to return values through argument
// references; if they do, they should be appropriately handled locally.
//
// %apply int &OUTPUT { int & };
// %apply float &OUTPUT { float & };
// %apply double &OUTPUT { double & };

// %array_class(float, floatArray);
// %array_class(double, doubleArray);


// Mapping C++ exceptions to Python

#if !defined(NO_SWIG_LSST_EXCEPTIONS)

%pythoncode %{
    import lsst.pex.exceptions
%}

%{
#include <new>
#include "lsst/pex/exceptions/Exception.h"
#include "lsst/pex/exceptions/Runtime.h"
%}

// Ignore commonly-used boost idiom to prevent warnings and avoid the need for
// even more %imports.
%ignore boost::noncopyable;
namespace boost {
    class noncopyable { };
}

// Make types from boost::cstdint known to SWIG
namespace boost {
    using ::int8_t;
    using ::uint8_t;
    using ::int16_t;
    using ::uint16_t;
    using ::int32_t;
    using ::uint32_t;
    using ::int64_t;
    using ::uint64_t;
}

// Use the Python C API to raise an exception of type
// lsst.pex.exceptions.Exception with a value that is a SWIGged proxy for a
// copy of the exception object.
%{
static void raiseLsstException(lsst::pex::exceptions::Exception& ex) {
    PyObject* pyex = 0;
    swig_type_info* tinfo = SWIG_TypeQuery(ex.getType());
    if (tinfo != 0) {
	lsst::pex::exceptions::Exception* e = ex.clone();
        pyex = SWIG_NewPointerObj(static_cast<void*>(e), tinfo,
            SWIG_POINTER_OWN);
    } else {
        PyErr_SetString(PyExc_RuntimeError, const_cast<char*>(ex.what()));
	return;
    }

    PyObject* pyexbase = PyExc_RuntimeError;
    PyObject* module = PyImport_AddModule("lsst.pex.exceptions");
    if (module != 0) {
        pyexbase = PyObject_GetAttrString(module, "LsstCppException");
        if (pyexbase == 0) {
            pyexbase = PyExc_RuntimeError;
        }
    }

    PyErr_SetObject(pyexbase, pyex);
}

%}

#endif

// Turns on the default C++ to python exception handling interface
%define %lsst_exceptions()
    %exception {
        try {
            $action
        } catch (lsst::pex::exceptions::Exception &e) {
            raiseLsstException(e);
            SWIG_fail;
        } catch (std::exception & e) {
            PyErr_SetString(PyExc_Exception, e.what());
            SWIG_fail;
        }
    }
%enddef


// Throw an exception if func returns NULL
%define NOTNULL(func)
    %exception func {
        $action;
        if (result == NULL) {
            $cleanup;
        }
    }
%enddef

// Throw an exception if func returns a negative value
%define NOTNEGATIVE(func)
    %exception func {
        $action;
        if (result < 0) {
            $cleanup;
        }
    }
%enddef

// convert void pointer to (TYPE *)
%define CAST(TYPE)
    %pointer_cast(void *, TYPE *, cast_ ## TYPE ## Ptr);
%enddef

