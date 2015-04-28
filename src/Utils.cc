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
/*!
 * Return a version name given an SVN HeadURL
 *
 * Given a string of the form
 *   Dollar HeadURL: svn+ssh://svn.lsstcorp.org/DC2/fw/tags/1.1/foo Dollar
 * (where I've written Dollar to foil svn) try to guess the version.
 *
 *    If the string is misformed, return "(NOSVN)";
 *
 *    If the version appears to be on the trunk, return "svn"
 *    as this is presumably an untagged * version
 *
 *    If the version appears to be in branches, tags, or tickets return
 *    the version string (with " B", "", or " T" appended respectively)
 *
 *    Otherwise return the svn URL
 *
 * Note: for this to be set by svn, you'll have to set the svn property
 * svn:keywords to expand HeadURL in the file where the HeadURL originates.
 */
void guessSvnVersion(std::string const& headURL, //!< the HeadURL String
                     std::string& version //!< the desired version
                    ) {
    const boost::regex getURL("^\\$HeadURL:\\s+([^$ ]+)\\s*\\$$");
    boost::smatch matchObject;
    if (boost::regex_search(headURL, matchObject, getURL)) {
        version = matchObject[1];

        const boost::regex getVersion("(branches|tags|tickets|trunk)/([^/]+)");
        if (boost::regex_search(version, matchObject, getVersion)) {
            std::string type = matchObject[1];
            version = matchObject[2];
        
            if (type == "branches") {
                version += "B";
            } else if (type == "tickets") {
                version += "T" ;
            } else if (type == "trunk") {
                version = "svn";
            }
        }
    } else {
        version = "(NOSVN)";
        return;
    }
}


// Free utility function

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
