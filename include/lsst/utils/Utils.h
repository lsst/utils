// -*- lsst-c++ -*-
//! \file
//! \defgroup mwi LSST framework 
//! \brief Generic LSST software support
//!
#if !defined(LSST_UTILS_H)
#define LSST_UTILS_H 1

//! Start a namespace without confusing emacs
//! \sa LSST_END_NAMESPACE
#define LSST_START_NAMESPACE(NAME) namespace NAME {
//! End a namespace without confusing emacs
//! \sa LSST_START_NAMESPACE
#define LSST_END_NAMESPACE(NAME) }

#include <string>
#include <boost/any.hpp>

//! \namespace lsst::utils
//\brief LSST utilities
LSST_START_NAMESPACE(lsst)
LSST_START_NAMESPACE(mwi)
LSST_START_NAMESPACE(utils)

void guessSvnVersion(const std::string &, std::string &OUTPUT);
boost::any stringToAny(std::string valueString);

LSST_END_NAMESPACE(utils)
LSST_END_NAMESPACE(mwi)
LSST_END_NAMESPACE(lsst)

#endif

