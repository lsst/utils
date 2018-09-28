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
