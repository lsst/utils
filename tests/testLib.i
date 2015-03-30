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
 
%define testLib_DOCSTRING
"
Test module for various utilities in p_lsstSwig.i and lsstNumPy.i
"
%enddef

%feature("autodoc", "1");
%module(package="testLib", docstring=testLib_DOCSTRING) testLib

%pythonnondynamic;
%naturalvar;  // use const reference typemaps

%include "lsst/p_lsstSwig.i"
%include "lsst/lsstNumPy.i"

%lsst_exceptions()

%initializeNumPy(utils_tests_testLib)

%returnNone(Example::get1)
%returnSelf(Example::get2)
%returnCopy(Example::get3)
%addStreamRepr(Example)
%useValueEquality(Example)

%{
#include <limits>
%}

%inline %{
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

#ifndef SWIG
    inline std::ostream & operator<<(std::ostream & os, Example const & ex) {
        return os << "Example(" << ex.getValue() << ")";
    }
#endif

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

%}

%template(accept_float32) acceptNumber<float>;
%template(accept_float64) acceptNumber<double>;
%template(accept_uint8) acceptNumber<unsigned char>;
%template(accept_uint16) acceptNumber<unsigned short>;
%template(accept_uint32) acceptNumber<unsigned int>;
%template(accept_uint64) acceptNumber<unsigned long long>;
%template(accept_int8) acceptNumber<signed char>;
%template(accept_int16) acceptNumber<short>;
%template(accept_int32) acceptNumber<int>;
%template(accept_int64) acceptNumber<long long>;

%template(accept_cref_float32) acceptNumberConstRef<float>;
%template(accept_cref_float64) acceptNumberConstRef<double>;
%template(accept_cref_uint8) acceptNumberConstRef<unsigned char>;
%template(accept_cref_uint16) acceptNumberConstRef<unsigned short>;
%template(accept_cref_uint32) acceptNumberConstRef<unsigned int>;
%template(accept_cref_uint64) acceptNumberConstRef<unsigned long long>;
%template(accept_cref_int8) acceptNumberConstRef<signed char>;
%template(accept_cref_int16) acceptNumberConstRef<short>;
%template(accept_cref_int32) acceptNumberConstRef<int>;
%template(accept_cref_int64) acceptNumberConstRef<long long>;
