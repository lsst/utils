// -*- lsst-c++ -*-
//! @file
//! @defgroup utils LSST general-purpose utilities
//! @brief Generic LSST software support
//!
#if !defined(LSST_UTILS_UTILS_H)
#define LSST_UTILS_UTILS_H 1

#include <string>
#include <boost/any.hpp>

//! @namespace lsst::utils
//@brief LSST utilities
namespace lsst {
namespace utils {

void guessSvnVersion(std::string const& headURL, std::string& OUTPUT);
boost::any stringToAny(std::string valueString);

}} // namespace lsst::utils

#endif

