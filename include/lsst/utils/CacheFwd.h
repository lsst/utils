#ifndef LSST_UTILS_CACHE_FWD_H
#define LSST_UTILS_CACHE_FWD_H

/** Forward declarations for lsst::utils::Cache
 *
 * For details on the Cache class, see the Cache.h file.
 */

#include <functional>  // std::equal_to, std::hash

namespace lsst {
namespace utils {

template <typename Key, typename Value, typename KeyHash=std::hash<Key>,
          typename KeyPred=std::equal_to<Key>>
class Cache;

}} // namespace lsst::utils

#endif // ifndef LSST_UTILS_CACHE_FWD_H
