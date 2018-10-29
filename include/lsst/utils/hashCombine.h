/*
 * LSST Data Management System
 * See COPYRIGHT file at the top of the source tree.
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
#ifndef LSST_UTILS_HASH_COMBINE_H
#define LSST_UTILS_HASH_COMBINE_H

#include <functional>

namespace lsst {
namespace utils {

/**
 * Combine hashes
 *
 * A specialization of hashCombine for a trivial argument list.
 */
inline std::size_t hashCombine(std::size_t seed) noexcept { return seed; }

/**
 * Combine hashes
 *
 * This is provided as a convenience for those who need to hash a composite.
 * C++11 includes std::hash, but neglects to include a facility for
 * combining hashes.
 *
 * @tparam T, Rest the types to hash. All types must have a valid (in
 *                 particular, non-throwing) specialization of std::hash.
 *
 * @param seed An arbitrary starting value.
 * @param value, rest The objects to hash.
 * @returns A combined hash for all the arguments after `seed`.
 *
 * @exceptsafe Shall not throw exceptions.
 *
 * To use it:
 *
 *     // Arbitrary seed; can change to get different hashes of same argument list
 *     std::size_t seed = 0;
 *     result = hashCombine(seed, obj1, obj2, obj3);
 */
// This implementation is provided by Matteo Italia, https://stackoverflow.com/a/38140932/834250
// Algorithm described at https://stackoverflow.com/a/27952689
// WARNING: should not be inline or constexpr; it can cause instantiation-order problems with std::hash<T>
template <typename T, typename... Rest>
std::size_t hashCombine(std::size_t seed, const T& value, Rest... rest) noexcept {
    std::hash<T> hasher;
    seed ^= hasher(value) + 0x9e3779b9 + (seed << 6) + (seed >> 2);
    return hashCombine(seed, rest...);
}

/**
 * Combine hashes in an iterable.
 *
 * This is provided as a convenience for those who need to hash a container.
 *
 * @tparam InputIterator an iterator to the objects to be hashed. The
 *                       pointed-to type must have a valid (in particular,
 *                       non-throwing) specialization of std::hash.
 *
 * @param seed An arbitrary starting value.
 * @param begin, end The range to hash.
 * @returns A combined hash for all the elements in [begin, end).
 *
 * @exceptsafe Shall not throw exceptions.
 *
 * To use it:
 *
 *     // Arbitrary seed; can change to get different hashes of same argument list
 *     std::size_t seed = 0;
 *     result = hashIterable(seed, container.begin(), container.end());
 */
// Note: not an overload of hashCombine to avoid ambiguity with hashCombine(size_t, T1, T2)
// WARNING: should not be inline or constexpr; it can cause instantiation-order problems with std::hash<T>
template <typename InputIterator>
std::size_t hashIterable(std::size_t seed, InputIterator begin, InputIterator end) noexcept {
    std::size_t result = 0;
    for (; begin != end; ++begin) {
        result = hashCombine(result, *begin);
    }
    return result;
}

}} // namespace lsst::utils

#endif
