#include "lsst/utils/python/Cache.h"

PYBIND11_PLUGIN(_cache) {
    py::module mod("_cache");
    lsst::utils::Cache<int, std::string> cache;
    lsst::utils::python::declareCache<int, std::string>(mod, "NumbersCache");
    return mod.ptr();
}
