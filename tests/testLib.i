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
Test module for various utilities in p_lsstSwig.i
"
%enddef

%feature("autodoc", "1");
%module(package="testLib", docstring=testLib_DOCSTRING) testLib

%{
#include <new>
#include <stdexcept>
#include "lsst/pex/exceptions.h"
%}

%pythonnondynamic;
%naturalvar;  // use const reference typemaps

%include "lsst/p_lsstSwig.i"

%lsst_exceptions()

%returnNone(Example::get1)
%returnSelf(Example::get2)
%returnCopy(Example::get3)
%addStreamRepr(Example)
%useValueEquality(Example)

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

    private:
        std::string _value;
    };

#ifndef SWIG
    inline std::ostream & operator<<(std::ostream & os, Example const & ex) {
        return os << "Example(" << ex.getValue() << ")";
    }
#endif

    void raiseException(std::string const &name) {
        if (name == "lsstException") {
            throw LSST_EXCEPT(lsst::pex::exceptions::RuntimeErrorException, name);
        } else if (name == "invalid_argument") {
            throw std::invalid_argument(name);
        } else if (name == "out_of_range") {
            throw std::out_of_range(name);
        } else if (name == "logic_error") {
            throw std::logic_error(name);
        } else if (name == "range_error") {
            throw std::range_error(name);
        } else if (name == "overflow_error") {
            throw std::overflow_error(name);
        } else if (name == "runtime_error") {
            throw std::runtime_error(name);
        } else if (name == "bad_alloc") {
            throw std::bad_alloc();
        } else if (name == "exception") {
            throw std::exception();
        }
    }
%}
