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
%include "std_shared_ptr.i"
%include "carrays.i"
%include "typemaps.i"

%include "lsst/base.h"

%include "lsst/lsstNumPy.i"

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

%include "lsst/pex/exceptions/handler.i"

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

// std_vector.i is broken when using %shared_ptr(std::vector<...>),
// apparently because %typemap_traits_ptr() overwrites typemaps setup
// by %shared_ptr. Therefore, create a std::vector specialization visible
// only to swig for a specific type, and move the %typemap_traits_ptr()
// invocation post-vector-method expansion.
//
// Note that macros should be invoked in the following order:
//
// %shared_vec(T);
// %shared_ptr(std::vector<T>);
// %include "header/file/for/T.h"
// %template(VecOfT) std::vector<T>;
//
%define %shared_vec(TYPE...)
    namespace std {
        template <class _Alloc >
        class vector<TYPE, _Alloc > {
        public:
            typedef size_t size_type;
            typedef ptrdiff_t difference_type;
            typedef TYPE value_type;
            typedef value_type* pointer;
            typedef const value_type* const_pointer;
            typedef TYPE& reference;
            typedef const TYPE& const_reference;
            typedef _Alloc allocator_type;

            %traits_swigtype(TYPE);

            %fragment(SWIG_Traits_frag(std::vector<TYPE, _Alloc >), "header",
                      fragment=SWIG_Traits_frag(TYPE),
                      fragment="StdVectorTraits") {
                namespace swig {
                    template <>  struct traits<std::vector<TYPE, _Alloc > > {
                        typedef pointer_category category;
                        static const char* type_name() {
                            return "std::vector<" #TYPE " >";
                        }
                    };
                }
            }

            %swig_vector_methods(std::vector<TYPE, _Alloc >);
            %std_vector_methods(vector);

            %typemap_traits_ptr(SWIG_TYPECHECK_VECTOR, std::vector<TYPE, _Alloc >);
        };
    }
%enddef

// Define Python __eq__ and __ne__ operators based on C++ operator==/!= overload.
%define %useValueEquality(CLS...)
%ignore CLS::operator==;  // just to quiet warnings
%ignore CLS::operator!=;  // just to quiet warnings
%extend CLS {
    bool _eq_impl(CLS const & other) const {
        return *self == other;
    }
    bool _ne_impl(CLS const & other) const {
        return *self != other;
    }
    %pythoncode %{
        def __eq__(self, rhs):
            try:
                return self._eq_impl(rhs)
            except Exception:
                return NotImplemented
        def __ne__(self, rhs):
            try:
                return self._ne_impl(rhs)
            except Exception:
                return NotImplemented
   %}
}
%enddef

// Define Python __eq__ and __ne__ operators based on C++ pointer equality.
%define %usePointerEquality(CLS...)
%ignore CLS::operator==;  // just to quiet warnings
%ignore CLS::operator!=;  // just to quiet warnings
%extend CLS {
    bool _eq_impl(CLS const * other) const {
        return self == other;
    }
    %pythoncode %{
        def __eq__(self, rhs):
            try:
                return self._eq_impl(rhs)
            except Exception:
                return NotImplemented
        def __ne__(self, rhs):
            return not self == rhs
   %}
}
%enddef 
// Adds __repr__ and __str__ to a class, assuming a stream operator<< has been provided.
%define %addStreamRepr(CLS...)
%{
#include <sstream>
%}
%extend CLS {
    std::string __repr__() const {
        std::ostringstream os;
        os << (*self);
        return os.str();
    }
    std::string __str__() const {
        std::ostringstream os;
        os << (*self);
        return os.str();
    }
}
%enddef

// Causes a Python wrapper for a function or member function to return None,
// regardless of what its C++ signature is.  Very useful for fixing up
// methods that unsafely return *this.
%define %returnNone(FUNC)
%feature("pythonappend") FUNC %{ val = None %}
%enddef

// Causes a Python wrapper for a function or member function to return 'self' in a safe way.
%define %returnSelf(FUNC)
%feature("pythonappend") FUNC %{ val = self %}
%enddef

// Causes a Python wrapper for a function of member function to return a copy.
// This can be used to make a C++ member function that returns a data member
// by reference safe in Python.  It is implemented by calling the copy
// constructor in Python, and hence will only work if the copy constructor
// has been wrapped.
%define %returnCopy(FUNC)
%feature("pythonappend") FUNC %{ val = type(val)(val) %}
%enddef

//
// Macro to add support for dynamic_cast in Python.  Should be added to all polymorphic
// derived classes wrapped with %shared_ptr.
//
// Unfortunately, this macro is a bit tricky to use on templated classes with more than
// one template parameter, as Swig's preprocessor can't handle the extra commas in the
// macro arguments.  In those cases, use an extra level of macro indirection:
//
//   template <typename T, typename U> class Foo : public Bar {}; // exposition
//   #define ARGS T, U
//   %castShared(Foo<ARGS>, Bar)
//   #undef ARGS
//
%define %castShared(DERIVED, BASE)
    %extend DERIVED {
        static std::shared_ptr< DERIVED > cast(std::shared_ptr< BASE > p) {
            return std::dynamic_pointer_cast< DERIVED >(p);
        }
    }
%enddef
