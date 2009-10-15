
#include "lsst/utils/RaDecStr.h"

using namespace std;
namespace except = lsst::pex::exceptions;

/**
 \defgroup RaDec  Right Ascension and Declination Parsers

\brief Routines for converting right ascension and declination from degrees or
radians into strings and back again.

Right ascensions and declinations (raDecs) are easiest read as strings
in the form hh:mm:ss.ss +dd:mm::ss.s, but for calculations, they need
to be in degrees or radians. These functions perform those calculations. 
The function names themselves use the following abbreviations

- <STRONG>ra</STRONG> Right Ascension
- <STRONG>dec</STRONG> Declination
- <STRONG>str</STRONG> String
- <STRONG>deg</STRONG> Degrees
- <STRONG>rad</STRONG> Radians.

So, for example raStrToRad() converts a right ascension in the form of a string to
radians.

The ouput strings are in fixed length Ra = hh:mm:ss.ss and Dec= +dd:mm::ss.s
with all zeros present (not replaced with whitespace).

Input strings must be of a similar format, although some variation is allowed.
The default delimiter (the colon) can be supplied as an optional argument
 @{
*/


using namespace std;
namespace ut = lsst::utils;

double radToDeg(long double angleInRadians) {
    const long double pi = 3.141592653589793115997963468544;
    return angleInRadians * 180./pi;
}


double degToRad(long double angleInDegrees) {
    const long double pi = 3.141592653589793115997963468544;
    return angleInDegrees * pi / 180.;
}


///Convert a right ascension in radians to a string format
///\param raRad Ra in radians
string ut::raRadToStr(double raRad ) {
    return raDegToStr( radToDeg(raRad) );
}
    
string ut::raDegToStr(double raDeg){

    double ra = raDeg;  //Shorthand
    
    //Convert to seconds of arc
    ra = round(ra*1e6)/1e6;
    ra *= 86400/360;
    
    int hr = (int) floor(ra/3600.);
    ra -= hr*3600;
    
    int mn = (int) floor(ra/60.);
    ra -= mn*60;    //Only seconds remain
    
    return str( boost::format("%02i:%02i:%05.2f") % hr % mn % ra);
}
    

string ut::decRadToStr(double decRad) {
    return decDegToStr( radToDeg(decRad) );
}

    
string ut::decDegToStr(double decDeg) {

    double dec = decDeg;    //Shorthand
    
    string sgn = (dec<0) ? "-" : "+";

    //Rounding the declination prevents 14.999999999 being represented
    //as 14.:59:60.00
    dec = fabs(round(dec*1e6)/1e6);

    int degrees = (int) floor(dec);
    dec -= degrees;

    int min = (int) floor(dec*60);
    dec -= min/60.;

    double sec = dec*3600;
    sec = floor(sec*100)/100.;

    string str = sgn;
    return boost::str(boost::format("%s%02i:%02i:%05.2f") % sgn % degrees % min % sec);
   
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


    

    
// ////////////////////////////////////////////////////////////////

//
// Converting strings to numbers
//

double ut::raStrToRad(std::string raStr, std::string delimiter) {
    return degToRad( raStrToDeg(raStr) );
}


double ut::raStrToDeg(std::string raStr, std::string delimiter) {
    
    //Regex the hours, minutes and seconds
    string regexStr = "(\\d+)";
    regexStr.append(delimiter);
    regexStr.append("(\\d+)");
    regexStr.append(delimiter);    
    regexStr.append("([\\d\\.]+)");
    
         static const boost::regex re(regexStr);
    boost::cmatch what;
    //This throws an exception of failure. I could catch it, 
    //but I'd only throw it again
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


double ut::decStrToRad(std::string decStr, std::string delimiter) {
    return degToRad( decStrToDeg(decStr) );
}


double ut::decStrToDeg(std::string decStr, std::string delimiter) {
    
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

/*@}*/
