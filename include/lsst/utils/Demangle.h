// -*- lsst-c++ -*-
#if !defined(LSST_DEMANGLE)             //! multiple inclusion guard macro
#define LSST_DEMANGLE 1

#include "lsst/mwi/utils/Utils.h"

namespace lsst {
namespace mwi {
namespace utils {

std::string demangleType(const std::string _typeName);
    
} // namespace utils
} // namespace mwi
} // namespace lsst
#endif
