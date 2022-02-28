option(ENABLE_CPPCHECK "Search for cppcheck and enable if available" ON)

if(ENABLE_CPPCHECK)
  find_program(CPPCHECK NAMES "cppcheck")
  if(CPPCHECK)
    set(CMAKE_CXX_CPPCHECK
        "${CPPCHECK};--std=c++11;--error-exitcode=1;--library=googletest")
  else()
    message(STATUS "Couldn't find cppcheck")
  endif()
endif()
