cmake_minimum_required(VERSION 3.16)

project(example)

add_executable(sample_bin sample.cpp)
add_test(NAME SampleBin COMMAND sample_bin)
if(CODE_COVERAGE)
  target_code_coverage(sample_bin AUTO ALL)
endif()
