#if !defined(LSST_TR1_UNORDERED_MAP_H)
#define LSST_TR1_UNORDERED_MAP_H

#if LSST_HAVE_TR1
#include <tr1/unordered_map>
#else
#include <ext/hash_map>

namespace __gnu_cxx {
    template<> class hash<std::string> {
    public:
        size_t operator()(std::string const& s) const {
            return __gnu_cxx::hash<char const*>()(s.c_str());
        }
    };
}

namespace std {
    namespace tr1 {
        template <typename KEY_t, typename VAL_t>
        class unordered_map : public __gnu_cxx::hash_map<KEY_t, VAL_t> {
        };
    }
}
#endif

#endif
