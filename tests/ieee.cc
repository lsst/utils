// -*- LSST-C++ -*-

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
        BOOST_CHECK(lsst::utils::fpclassify(inf) == FP_INFINITE); \
        \
        TYPE nan = std::numeric_limits<TYPE>::quiet_NaN();      \
        BOOST_CHECK(lsst::utils::isnan(nan)); \
        BOOST_CHECK(!lsst::utils::isfinite(nan)); \
        BOOST_CHECK(lsst::utils::fpclassify(nan) == FP_NAN); \
    } while(0)

BOOST_AUTO_TEST_CASE(IeeeBasic) { /* parasoft-suppress  LsstDm-3-2a LsstDm-3-4a LsstDm-4-6 LsstDm-5-25 "Boost non-Std" */
    CHECK_CMATH(float);
    CHECK_CMATH(double);
    CHECK_CMATH(long double);
}
