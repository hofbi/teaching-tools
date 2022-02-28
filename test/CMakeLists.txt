include(CodeProfiling)

# Unit Tests
add_executable(unittests example/simple_test.cpp)

target_link_libraries(unittests PRIVATE gtest_main)

# CTest
gtest_discover_tests(unittests)

if(CODE_COVERAGE)
  target_code_coverage(unittests AUTO ALL)
endif()

# Code Profiling
addcallgrindtarget(unittests)
addmemchecktarget(unittests)
