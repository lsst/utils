// -*- lsst-c++ -*-
#if !defined(LSST_UTILS_DEMANGLE_H)
#define LSST_UTILS_DEMANGLE_H 1

#include <string>

namespace lsst {
namespace utils {

std::string demangleType(std::string const _typeName);
    
}} // namespace lsst::utils
#endif
