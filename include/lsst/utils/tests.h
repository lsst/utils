// -*- lsst-c++ -*-

/*
 * This file is part of utils.
 *
 * Developed for the LSST Data Management System.
 * This product includes software developed by the LSST Project
 * (https://www.lsst.org).
 * See the COPYRIGHT file at the top-level directory of this distribution
 * for details of code ownership.
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
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

#ifndef LSST_UTILS_TESTS_H
#define LSST_UTILS_TESTS_H

// Do not include unit_test.hpp, to avoid definition problems with BOOST_TEST_MODULE

#include <ostream>
#include <type_traits>

namespace lsst {
namespace utils {

namespace {
// Variable template reporting whether a type can be printed using <<
// Second template parameter is a dummy to let us do some metaprogramming
template <typename, typename = void>
constexpr bool HAS_STREAM_OUTPUT = false;
template <typename T>
constexpr bool HAS_STREAM_OUTPUT<
        T, std::enable_if_t<true, decltype((void)(std::declval<std::ostream&>() << std::declval<T&>()),
                                           void())>> = true;

// Conditional function templates reporting object values if possible
template <typename T, class Hash>
std::enable_if_t<HAS_STREAM_OUTPUT<T>> printIfHashEqual(T obj1, T obj2, Hash hash) {
    BOOST_TEST_REQUIRE(obj1 == obj2);
    BOOST_TEST(hash(obj1) == hash(obj2),
               obj1 << " == " << obj2 << ", but " << hash(obj1) << " != " << hash(obj2));
}
template <typename T, class Hash>
std::enable_if_t<!HAS_STREAM_OUTPUT<T>> printIfHashEqual(T obj1, T obj2, Hash hash) {
    if (!(obj1 == obj2)) {
        BOOST_FAIL("Unequal objects need not have equal hashes.");
    }
    BOOST_TEST(hash(obj1) == hash(obj2));
}
}  // namespace

/**
 * Compile-time test of whether a specialization of std::hash conforms to the
 * general spec.
 *
 * The function itself is a no-op.
 *
 * @tparam T The properties of `std::hash<T>` will be tested.
 */
template <typename T>
constexpr void assertValidHash() {
    using namespace std;
    using Hash = hash<remove_cv_t<T>>;

    static_assert(is_default_constructible<Hash>::value,
                  "std::hash specializations must be default-constructible");
    static_assert(is_copy_assignable<Hash>::value, "std::hash specializations must be copy-assignable");
    // Swappability hard to test before C++17
    static_assert(is_destructible<Hash>::value, "std::hash specializations must be destructible");

    static_assert(is_same<typename Hash::argument_type, remove_cv_t<T>>::value,
                  "std::hash must have an argument_type member until C++20");
    static_assert(is_same<typename Hash::result_type, size_t>::value,
                  "std::hash must have a result_type member until C++20");
    // Ability to call Hash(T) hard to test before C++17
    static_assert(is_same<result_of_t<Hash(T)>, size_t>::value,
                  "std::hash specializations must be callable and return a size_t");
}

/**
 * Test that equal objects have equal hashes.
 *
 * If objects of type `T` can be equal despite having different internal
 * representations, you should include pairs of such objects.
 *
 * @tparam T A hashable type.
 *
 * @param obj1, obj2 Two equal objects.
 */
template <typename T>
void assertHashesEqual(T obj1, T obj2) {
    using Hash = std::hash<std::remove_cv_t<T>>;

    printIfHashEqual(obj1, obj2, Hash());
}

}  // namespace utils
}  // namespace lsst

#endif
