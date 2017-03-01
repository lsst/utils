// -*- LSST-C++ -*-

/*
 * LSST Data Management System
 * Copyright 2008-2015 AURA/LSST.
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
 * see <https://www.lsstcorp.org/LegalNotices/>.
 */

#include <cstddef>
#include <utility>
#include <ostream>
#include <iostream>

#define BOOST_TEST_DYN_LINK
#define BOOST_TEST_MODULE pybind11

#include "boost/test/unit_test.hpp"

#include "lsst/pex/exceptions.h"
#include "lsst/utils/python.h"

using lsst::utils::python::cppIndex;
using OutOfRangeError = lsst::pex::exceptions::OutOfRangeError;
using sizet_pair = std::pair<std::size_t, std::size_t>;

// In order to use boost_test to compare std::pairs: operator<< must be defined for the pair in question
// and a templated print_loc_value added to boost::test_tools::tt_detail to refer to it, as per:
// http://stackoverflow.com/questions/17572583/boost-check-fails-to-compile-operator-for-custom-types/17573165#17573165

std::ostream& operator<<(std::ostream& os, sizet_pair const& pair) {
    os << "(" << pair.first << ", " << pair.second << ")";
    return os;
}

namespace boost {
namespace test_tools {
namespace tt_detail {

template <>
struct print_log_value<sizet_pair> {
    void operator()(std::ostream& os, sizet_pair const& pair) { ::operator<<(os, pair); }
};

}  // namespace tt_detail
}  // namespace test_tools
}  // namespace boost

/// Test the 1-argument version of lsst::utils::cppIndex
BOOST_AUTO_TEST_CASE(cppInde1) {
    // loop over various sizes
    // note that when size == 0 no indices are valid, but the "invalid indices" tests still run
    for (int size = 0; size < 4; ++size) {
        // loop over all valid indices
        for (int ind = 0; ind < size; ++ind) {
            // the negative index that points to the same element as ind
            // for example if size = 3 and ind = 2 then negind = -1
            int negind = ind - size;

            BOOST_CHECK_EQUAL(cppIndex(size, ind), ind);
            BOOST_CHECK_EQUAL(cppIndex(size, negind), ind);
        }
        // invalid indices (the two closest to zero)
        BOOST_CHECK_THROW(cppIndex(size, size), OutOfRangeError);
        BOOST_CHECK_THROW(cppIndex(size, -size - 1), OutOfRangeError);
    }
}

/// Test the 2-argument version of lsst::utils::cppIndex
BOOST_AUTO_TEST_CASE(cppIndex2) {
    // loop over various sizes;
    // if either size is 0 then no pairs of indices are valid, but the "both indices invalid" tests still run
    for (int size0 = 0; size0 < 4; ++size0) {
        for (int size1 = 0; size1 < 4; ++size1) {
            // the first (closest to 0) invalid negative indices
            int negbad0 = -size0 - 1;  
            int negbad1 = -size1 - 1;

            // loop over all valid indices
            for (int ind0 = 0; ind0 < size0; ++ind0) {
                for (int ind1 = 0; ind1 < size1; ++ind1) {
                    // negative indices that point to the same element as the positive index
                    int negind0 = ind0 - size0;
                    int negind1 = ind1 - size1;

                    // both indeces valid
                    BOOST_CHECK_EQUAL(cppIndex(size0, size1, ind0, ind1), sizet_pair(ind0, ind1));
                    BOOST_CHECK_EQUAL(cppIndex(size0, size1, ind0, negind1), sizet_pair(ind0, ind1));
                    BOOST_CHECK_EQUAL(cppIndex(size0, size1, negind0, ind1), sizet_pair(ind0, ind1));
                    BOOST_CHECK_EQUAL(cppIndex(size0, size1, negind0, negind1), sizet_pair(ind0, ind1));

                    // one index invalid
                    BOOST_CHECK_THROW(cppIndex(size0, size1, ind0, size1), OutOfRangeError);
                    BOOST_CHECK_THROW(cppIndex(size0, size1, ind0, negbad1), OutOfRangeError);
                    BOOST_CHECK_THROW(cppIndex(size0, size1, size0, ind1), OutOfRangeError);
                    BOOST_CHECK_THROW(cppIndex(size0, size1, negbad0, ind1), OutOfRangeError);
                }
            }
            // both indices invalid (just test the invalid indices closest to 0)
            BOOST_CHECK_THROW(cppIndex(size0, size1, size0, size1), OutOfRangeError);
            BOOST_CHECK_THROW(cppIndex(size0, size1, size0, -size1 - 1), OutOfRangeError);
            BOOST_CHECK_THROW(cppIndex(size0, size1, negbad0, size1), OutOfRangeError);
            BOOST_CHECK_THROW(cppIndex(size0, size1, negbad0, negbad1), OutOfRangeError);
        }
    }
}
