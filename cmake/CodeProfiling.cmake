function(addCallgrindTarget target)
  add_custom_target(
    callgrind_${target}
    COMMENT "Running callgrind analysis on ${target}"
    COMMAND ${MEMORYCHECK_COMMAND} --tool=callgrind $<TARGET_FILE:${target}>
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
    DEPENDS ${target})
endfunction()

function(addMemCheckTarget target)
  add_custom_target(
    memcheck_${target}
    COMMENT "Running valgrind memory analysis on ${target}"
    COMMAND
      ${MEMORYCHECK_COMMAND} --tool=memcheck --xml=yes
      --xml-file=valgrind_${target} --gen-suppressions=all --leak-check=full
      --leak-resolution=med --track-origins=yes $<TARGET_FILE:${target}>
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
    DEPENDS ${target})
endfunction()
