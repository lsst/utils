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
 
#include "lsst/utils/Utils.h"

#include <iostream>
#include <sstream>
#include <string>
#include "boost/regex.hpp"
#include "lsst/pex/exceptions.h"

namespace lsst {
namespace utils {

boost::any stringToAny(std::string valueString)
{
    const boost::regex intRegex("(\\Q+\\E|\\Q-\\E){0,1}[0-9]+");
    const boost::regex doubleRegex("(\\Q+\\E|\\Q-\\E){0,1}([0-9]*\\.[0-9]+|[0-9]+\\.[0-9]*)((e|E)(\\Q+\\E|\\Q-\\E){0,1}[0-9]+){0,1}");
    const boost::regex FitsStringRegex("'(.*)'");

    boost::smatch matchStrings;

    std::istringstream converter(valueString);

    if (boost::regex_match(valueString, intRegex)) {
        // convert the string to an int
        int intVal;
        converter >> intVal;
        return boost::any(intVal);
    }
        
    if (boost::regex_match(valueString, doubleRegex)) {
        // convert the string to a double
        double doubleVal;
        converter >> doubleVal;
        return boost::any(doubleVal);
    }

    if (boost::regex_match(valueString, matchStrings, FitsStringRegex)) {
        // strip off the enclosing single quotes and return the string
        return boost::any(matchStrings[1].str());
    }

    return boost::any(valueString);
}

std::string getPackageDir(std::string const& packageName) {
    std::string envVar = packageName;      // package's environment variable
    
    transform(envVar.begin(), envVar.end(), envVar.begin(), (int (*)(int)) toupper);
    envVar += "_DIR";
    
    char const *dir = getenv(envVar.c_str());
    if (!dir) {
        throw LSST_EXCEPT(lsst::pex::exceptions::NotFoundError, "Package " + packageName + " not found");
    }
    
    return dir;
}
    
}} // namespace lsst::utils
