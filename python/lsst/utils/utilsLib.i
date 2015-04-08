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
 
%define utils_DOCSTRING
"
Access to useful Utility classes.
"
%enddef

%feature("autodoc", "1");
%module(package="lsst.utils", docstring=utils_DOCSTRING) utilsLib

%{
#include "lsst/utils/Demangle.h"
#include "lsst/utils/Utils.h"
#include "lsst/utils/RaDecStr.h"
#include "lsst/pex/exceptions.h"
%}

%import "lsst/pex/exceptions/exceptionsLib.i"

%include "lsst/p_lsstSwig.i"
%initializeNumPy(utils)
%lsst_exceptions()

%include "lsst/utils/Demangle.h"
%include "lsst/utils/Utils.h"
%include "lsst/utils/RaDecStr.h"
