find_package(pybind11 REQUIRED)

install(
    DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/
    DESTINATION ${CMAKE_INSTALL_PREFIX}/python/lsst/utils
    FILES_MATCHING PATTERN "*.py"
)

add_custom_target(utils_version ALL
    ${CMAKE_COMMAND} -P ${CMAKE_CURRENT_SOURCE_DIR}/version.cmake
    BYPRODUCTS ${CMAKE_CURRENT_BINARY_DIR}/version.py
)

install(
    FILES ${CMAKE_CURRENT_BINARY_DIR}/version.py
    DESTINATION ${CMAKE_INSTALL_PREFIX}/python/lsst/utils
)
