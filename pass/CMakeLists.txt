find_package(LLVM REQUIRED CONFIG)
list(APPEND CMAKE_MODULE_PATH "${LLVM_CMAKE_DIR}")
include(AddLLVM)

add_llvm_pass_plugin(TracingPass tracing_pass.cpp BUILDTREE_ONLY PARTIAL_SOURCES_INTENDED)
target_compile_features(TracingPass PRIVATE cxx_std_17)
target_include_directories(TracingPass SYSTEM PRIVATE ${LLVM_INCLUDE_DIRS})
separate_arguments(LLVM_DEFINITION_FLAGS NATIVE_COMMAND "${LLVM_DEFINITIONS}")
target_compile_options(TracingPass PRIVATE ${LLVM_DEFINITION_FLAGS} -Os)
set_target_properties(TracingPass PROPERTIES
    PREFIX ""
    SUFFIX "${CMAKE_SHARED_MODULE_SUFFIX}"
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}"
)

if(NOT CMAKE_C_COMPILER_ID MATCHES "Clang")
    message(FATAL_ERROR "graphical_app_traced requires Clang")
endif()
if(NOT CMAKE_C_COMPILER_VERSION MATCHES "^${LLVM_VERSION_MAJOR}\\.")
    message(FATAL_ERROR "Clang and the LLVM pass must use the same major version (LLVM ${LLVM_VERSION_MAJOR})")
endif()

add_executable(graphical_app_traced ${APP_SOURCES} trace.c)
set_target_properties(graphical_app_traced PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${PROJECT_BINARY_DIR}"
)
set(APP_TRACED_SOURCE "${PROJECT_SOURCE_DIR}/app/src/app.c")
set_property(SOURCE "${APP_TRACED_SOURCE}" APPEND PROPERTY COMPILE_OPTIONS
    "-fpass-plugin=$<TARGET_FILE:TracingPass>"
)
add_dependencies(graphical_app_traced TracingPass)

# This directory's source properties affect only the traced target. Recompile
# app.c when the plugin changes, so future instrumentation stays current.
set_property(SOURCE "${APP_TRACED_SOURCE}" APPEND PROPERTY OBJECT_DEPENDS
    "${CMAKE_CURRENT_BINARY_DIR}/TracingPass${CMAKE_SHARED_MODULE_SUFFIX}"
)
