// -*- lsst-c++ -*-
//! @file
//! @defgroup utils LSST general-purpose utilities
//! @brief Generic LSST software support
//!
#if !defined(LSST_UTILS_IEEE_H)
#define LSST_UTILS_IEEE_H 1

#include <string>
#include "boost/math/special_functions/fpclassify.hpp"

//! @namespace lsst::utils
//@brief LSST utilities
namespace lsst { namespace utils {
/**
 * Provide an implementation of some IEEE math functions TR1, but not yet reliably available
 *
 * We use the same names as will someday be in C++, but in namepace lsst::utils
 */

/*
 * We use boost's fpclassify.hpp (which may in turn use the compiler's implementation of isnan if available),
 * but with one change.  Boost doesn't undefine e.g. isnan, but we do.  The parentheses in the definition of
 * e.g. lsst_isnan are to foil any attempt by the compiler to expand e.g. isnan as a macro.
 */
namespace {
    template <class T>
    int lsst_fpclassify(T t) {
        return (boost::math::fpclassify)(t);
    }
    
    template <class T>
    bool lsst_isfinite(T z) {           // Neither infinity nor NaN.
        return (boost::math::isfinite)(z);
    }

    template <class T>
    bool lsst_isinf(T t) {              // Infinity (+ or -).
        return (boost::math::isinf)(t);
    }

    template <class T>
    bool lsst_isnan(T t) {              // NaN.
        return (boost::math::isnan)(t);
    }

    template <class T>
    bool lsst_isnormal(T t) {           // isfinite and not denormalised.
        return (boost::math::isnormal)(t);
    }
}
/*
 * Now that we have defined e.g. lsst_isnan it's safe to undef any macros
 */
#if defined(fpclassify)
#   undef fpclassify
#endif
#if defined(isfinite)
#   undef isfinite
#endif
#if defined(isinf)
#   undef isinf
#endif
#if defined(isnan)
#   undef isnan
#endif
#if defined(isnormal)
#   undef isnormal
#endif

template <class T>
int fpclassify(T t) {
    return lsst_fpclassify(t);
}

template <class T>
int isfinite(T t) {
    return lsst_isfinite(t);
}

template <class T>
int isinf(T t) {
    return lsst_isinf(t);
}

template <class T>
int isnan(T t) {
    return lsst_isnan(t);
}

template <class T>
int isnormal(T t) {
    return lsst_isnormal(t);
}

}} // namespace lsst::utils

#endif
