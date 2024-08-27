cmake_minimum_required(VERSION 3.16)

project(SoftwareEngineeringLab)

# CMake Settings
set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)
include(FetchContent)

# Coverage Settings
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
  set(CODE_COVERAGE ON)
  include(CodeCoverage)
  add_code_coverage_all_targets(EXCLUDE /usr/* ${PROJECT_BINARY_DIR}/_deps/*)
  add_custom_target(
    coverage
    DEPENDS ccov-all
    COMMENT "Running coverage")
endif()

# Dependencies
include(UnitTesting)
include(ClangTidy)
include(CppCheck)
include(IALWYU)

# Source
add_subdirectory(source)

# Tests
add_subdirectory(test)
