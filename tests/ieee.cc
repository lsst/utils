// -*- LSST-C++ -*-
#include <iostream>
#include <limits>
#include <cmath>
#include "lsst/utils/ieee.h"

#define BOOST_TEST_DYN_LINK
#define BOOST_TEST_MODULE Ieee

#include "boost/test/unit_test.hpp"
#include "boost/test/floating_point_comparison.hpp"

#define CHECK_CMATH(TYPE) \
    do { \
        TYPE inf = std::numeric_limits<TYPE>::infinity();       \
        BOOST_CHECK(lsst::utils::isinf(inf)); \
        BOOST_CHECK(!lsst::utils::isfinite(inf)); \
        BOOST_CHECK(lsst::utils::fpclassify(inf) & FP_INFINITE); \
        \
        TYPE nan = std::numeric_limits<TYPE>::quiet_NaN();      \
        BOOST_CHECK(lsst::utils::isnan(nan)); \
        BOOST_CHECK(!lsst::utils::isfinite(nan)); \
        BOOST_CHECK(lsst::utils::fpclassify(nan) & FP_NAN); \
    } while(0)

BOOST_AUTO_TEST_CASE(IeeeBasic) { /* parasoft-suppress  LsstDm-3-2a LsstDm-3-4a LsstDm-4-6 LsstDm-5-25 "Boost non-Std" */
    CHECK_CMATH(float);
    CHECK_CMATH(double);
    CHECK_CMATH(long double);
}
