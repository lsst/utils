
#ifndef RA_DEC_STR_H
#define RA_DEC_STR_H

#include <string>
#include <cmath>

#include "boost/format.hpp"
#include "boost/regex.hpp"
#include "boost/lexical_cast.hpp"

#include "lsst/pex/exceptions/Runtime.h"

namespace lsst { namespace utils {


std::string raRadToStr(double raRad);
std::string decRadToStr(double decRad);

std::string raDegToStr(double raDeg);
std::string decDegToStr(double decDeg);

std::string raDecRadToStr(double raRad, double decRad);
std::string raDecDegToStr(double raDeg, double decDeg);


double raStrToRad(std::string raStr, std::string delimiter=":");
double raStrToDeg(std::string raStr, std::string delimiter=":"); 
    
double decStrToRad(std::string decStr, std::string delimiter=":");
double decStrToDeg(std::string decStr, std::string delimiter=":"); 

}}                 

#endif
