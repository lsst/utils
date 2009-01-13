#if !defined(LSST_TR1_UNORDERED_MAP_H)
#define LSST_TR1_UNORDERED_MAP_H

#include "boost/unordered_map.hpp"

namespace std {
    namespace tr1 {
        template <typename KEY_t, typename VAL_t>
        class unordered_map : public boost::unordered_map<KEY_t, VAL_t> {
        };
    }
}

#endif
