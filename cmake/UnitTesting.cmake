include(CTest)
enable_testing()

FetchContent_Declare(
  googletest
  GIT_REPOSITORY https://github.com/google/googletest.git
  GIT_TAG origin/main)

FetchContent_MakeAvailable(googletest)

include(GoogleTest)
