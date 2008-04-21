#include "lsst/utils/Utils.h"

#include <cctype>
#include <iostream>
#include <sstream>
#include <string>
#include <algorithm>
#include <boost/regex.hpp>
#include <stdexcept>

using namespace std;

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
void guessSvnVersion(string const& headURL, //!< the HeadURL String
                     string& version //!< the desired version
                    ) {
    const boost::regex getURL("^\\$HeadURL:\\s+([^$ ]+)\\s*\\$$");
    boost::smatch matchObject;
    if (boost::regex_search(headURL, matchObject, getURL)) {
        version = matchObject[1];

        const boost::regex getVersion("(branches|tags|tickets|trunk)/([^/]+)");
        if (boost::regex_search(version, matchObject, getVersion)) {
            string type = matchObject[1];
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

boost::any stringToAny(string valueString)
{
    const boost::regex intRegex("(\\Q+\\E|\\Q-\\E){0,1}[0-9]+");
    const boost::regex doubleRegex("(\\Q+\\E|\\Q-\\E){0,1}([0-9]*\\.[0-9]+|[0-9]+\\.[0-9]*)((e|E)(\\Q+\\E|\\Q-\\E){0,1}[0-9]+){0,1}");
    const boost::regex FitsStringRegex("'(.*)'");

    boost::smatch matchStrings;

    istringstream converter(valueString);

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

/*!
 * \brief return an eups PRODUCT_DIR
 *
 * Return the directory of a setup product
 *
 * \throws std::invalid_argument if version != "setup"
 * \throws std::runtime_error if desired version can't be found
 */
string eups::productDir(string const& product, string const& version) {
    if (version != "setup") {
        throw std::invalid_argument("Unsupported version: " + version);
    }

    string var = product;      // product's environment variable
    
    transform(var.begin(), var.end(), var.begin(), (int (*)(int)) toupper);
    var += "_DIR";

    char const *dir = getenv(var.c_str());
    if (!dir) {
        throw std::runtime_error("Product " + product + " has no version " + version);
    }

    return dir;
}

}} // namespace lsst::utils
