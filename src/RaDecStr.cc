
using namespace std;

#include "lsst/utils/RaDecStr.h"



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

double ut::raStrToRad(string raStr, string delimiter) {
    return degToRad( raStrToDeg(raStr) );
}


double ut::raStrToDeg(string raStr, string delimiter) {
    
    //Regex the hours, minutes and seconds
    string regexStr = "(\\d+)";
    regexStr.append(delimiter);
    regexStr.append("(\\d+)");
    regexStr.append(delimiter);    
    regexStr.append("(\\d+)");
    
    std::cout << regexStr << endl;
     //http://www.boost.org/doc/libs/1_40_0/libs/regex/doc/html/boost_regex/captures.html
    static const boost::regex re(regexStr);
    boost::regex_match(raStr, re);
    boost::smatch m;
    
    //Convert strings to doubles
    
    //Place holders, so code will compile (but tests will fail)
    double hours = boost::lexical_cast<double>(m.captures(0));
    double mins = 0;//boost::lexical_cast<double>(m[1]);
    double secs = 0;//boost::lexical_cast<double>(m[2]);
    
    double raDeg = sec/3600.;
    raDeg += mins/60.;
    raDeg += hours;
    raDeg *= 360./24.;
    
    return raDeg;
}


