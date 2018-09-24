#ifndef LSST_UTILS_HASH_COMBINE_H
#define LSST_UTILS_HASH_COMBINE_H

#include <functional>

namespace lsst {
namespace utils {

//@{
/** Combine hashes
 *
 * This is provided as a convenience for those who need to hash a composite.
 * C++11 includes std::hash, but neglects to include a facility for
 * combining hashes.
 *
 * To use it:
 *
 *    std::size_t seed = 0;
 *    result = hashCombine(seed, obj1, obj2, obj3);
 *
 * This solution is provided by Matteo Italia
 * https://stackoverflow.com/a/38140932/834250
 */
inline std::size_t hashCombine(std::size_t seed) { return seed; }

template <typename T, typename... Rest>
std::size_t hashCombine(std::size_t seed, const T& value, Rest... rest) {
    std::hash<T> hasher;
    seed ^= hasher(value) + 0x9e3779b9 + (seed << 6) + (seed >> 2);
    return hashCombine(seed, rest...);
}
//@}

}} // namespace lsst::utils

#endif
