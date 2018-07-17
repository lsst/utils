#include "lsst/utils/python/Cache.h"

PYBIND11_MODULE(_cache, mod) {
    lsst::utils::Cache<int, std::string> cache;
    lsst::utils::python::declareCache<int, std::string>(mod, "NumbersCache");
}
