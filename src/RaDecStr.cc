
#include "lsst/utils/RaDecStr.h"

using namespace std;
namespace except = lsst::pex::exceptions;



using namespace std;
namespace ut = lsst::utils;

inline double radToDeg(double angleInRadians) {
    const double pi = 3.141592653589793115997963468544;
    return angleInRadians * 180/pi;
}


inline double degToRad(double angleInDegrees) {
    const double pi = 3.141592653589793115997963468544;
    return angleInDegrees * pi / 180.;
}

string ut::raRadToStr(double raRad) {
    return raDegToStr( radToDeg(raRad) );
}
    
string ut::raDegToStr(double raDeg){

    double ra = raDeg;  //Shorthand
    
    //Convert to seconds of arc
    ra *= 86400/3600;
    
    int hr = (int) floor(raDeg/3600.);
    ra -= hr*3600;

    int mn = (int) floor(ra/60.);
    ra -= mn*60;    //Only seconds remain

    return str( boost::format("%2i:%02i:%5.2f") % hr % mn % ra);
}
    

string ut::decRadToStr(double decRad) {
    return decDegToStr( radToDeg(decRad) );
}

    
string ut::decDegToStr(double decDeg) {

    double dec = decDeg;    //Shorthand
    
    string sgn;
    if(dec < 0) {
        sgn="-";
    } else {
        sgn="+";
    }

    dec = fabs(dec);

    int degrees = (int) floor(dec);
    dec -= degrees;

    int min = (int) floor(dec*60);
    dec -= min/60.;

    double sec = dec*3600;

    string str = sgn;
    return str + boost::str(boost::format("%2i:%02i:%05.2f") %  degrees % min % sec);
   
}
    

string ut::raDecRadToStr(double raRad, double decRad) {
    string val = raRadToStr(raRad);
    val = val + " "+decRadToStr(decRad);
    return val;
}

    
string ut::raDecDegToStr(double raDeg, double decDeg) {
    string val = raDegToStr(raDeg);
    val = val + " "+decDegToStr(decDeg);
    return val;
}


    
    
// *********************************************************************

//
// Converting strings to numbers
//

#include <iostream>
#include <cstdio>
double ut::raStrToRad(string raStr, string delimiter) {
    return degToRad( raStrToDeg(raStr) );
}


double ut::raStrToDeg(string raStr, string delimiter) {
    
    //Regex the hours, minutes and seconds
    string regexStr = "(\\d+)";
    regexStr.append(delimiter);
    regexStr.append("(\\d+)");
    regexStr.append(delimiter);    
    regexStr.append("([\\d\\.]+)");
    
     //http://www.boost.org/doc/libs/1_40_0/libs/regex/doc/html/boost_regex/captures.html
    static const boost::regex re(regexStr);
    boost::cmatch what;
    //This throws an exception of failure. I could catch it, but I'd only throw it 
    //again
    if(! boost::regex_match(raStr.c_str(), what, re)) {
        string msg= boost::str(boost::format("Failed to parse %s as a declination") % raStr);
        throw LSST_EXCEPT(except::RuntimeErrorException, msg);
    }  
       

    //Convert strings to doubles. Again, errors thrown on failure
    double hours = boost::lexical_cast<double>(string(what[1].first, what[1].second));
    double mins = boost::lexical_cast<double>(string(what[2].first, what[2].second));
    double secs = boost::lexical_cast<double>(string(what[3].first, what[3].second));
    
    double raDeg = secs/3600.;
    raDeg += mins/60.;
    raDeg += hours;
    raDeg *= 360./24.;
    
    //printf("%g %g %g --> %g\n", hours, mins, secs, raDeg);
    return raDeg;

}


double ut::decStrToRad(string decStr, string delimiter) {
    return degToRad( decStrToDeg(decStr) );
}


double ut::decStrToDeg(string decStr, string delimiter) {
    
    //Regex the degrees, minutes and seconds
    string regexStr = "([\\d]+)";
    regexStr.append(delimiter);
    regexStr.append("(\\d+)");
    regexStr.append(delimiter);    
    regexStr.append("([\\d\\.]+)");
    
     //http://www.boost.org/doc/libs/1_40_0/libs/regex/doc/html/boost_regex/captures.html
    static const boost::regex re(regexStr);
    boost::cmatch what;

    if(! boost::regex_search(decStr.c_str(), what, re)) {
        string msg= boost::str(boost::format("Failed to parse %s as a declination") % decStr);
        throw LSST_EXCEPT(except::RuntimeErrorException, msg);
    }  

    //Convert strings to doubles. Automatically pass the exception up the stack
    double degrees = boost::lexical_cast<double>(string(what[1].first, what[1].second));
    double mins = boost::lexical_cast<double>(string(what[2].first, what[2].second));
    double secs = boost::lexical_cast<double>(string(what[3].first, what[3].second));
    
    degrees += ((secs/60.) +mins)/60.;
    
    //Search for the presence of a minus sign. This approach catches the case of -0 degrees
    string pmStr = "^-";
    static const boost::regex pm(pmStr);
    if(boost::regex_search(decStr, pm)) {
        degrees *= -1;
    }
    
    return degrees;
}
