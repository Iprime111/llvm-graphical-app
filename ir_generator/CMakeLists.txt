cmake_minimum_required(VERSION 3.20)

if(CMAKE_SOURCE_DIR STREQUAL CMAKE_CURRENT_SOURCE_DIR)
    project(app_ir_generator LANGUAGES C CXX)
endif()

find_package(LLVM REQUIRED CONFIG)
if(NOT LLVM_VERSION_MAJOR EQUAL 21)
    message(FATAL_ERROR "This generator supports LLVM 21")
endif()

include("${CMAKE_CURRENT_SOURCE_DIR}/../cmake/AppIR.cmake")
find_package(Python3 3.9 REQUIRED COMPONENTS Interpreter)
find_package(SDL2 REQUIRED CONFIG)
find_path(SDL2_ROOT_INCLUDE_DIR NAMES SDL2/SDL.h REQUIRED)

set(APP_IR_INPUT "${APP_IR_FILE}" CACHE FILEPATH "Input LLVM IR")
set(GENERATED_FUNCTION "${CMAKE_CURRENT_BINARY_DIR}/app_builder.inc")
set(GENERATOR_SCRIPTS_DIR "${CMAKE_CURRENT_SOURCE_DIR}/scripts")
set(GENERATOR_PYTHON_SOURCES
    "${GENERATOR_SCRIPTS_DIR}/generate.py"
    "${GENERATOR_SCRIPTS_DIR}/ir_parser.py"
)

add_custom_command(
    OUTPUT "${GENERATED_FUNCTION}"
    COMMAND "${Python3_EXECUTABLE}" "${GENERATOR_SCRIPTS_DIR}/generate.py"
            "${APP_IR_INPUT}" -o "${GENERATED_FUNCTION}"
    DEPENDS app_ir "${APP_IR_INPUT}" ${GENERATOR_PYTHON_SOURCES}
    COMMENT "Generating IRBuilder C++ from app.ll"
    VERBATIM
)
add_custom_target(app_ir_generator_sources DEPENDS "${GENERATED_FUNCTION}")
add_dependencies(app_ir_generator_sources app_ir)

set_source_files_properties("${GENERATED_FUNCTION}" PROPERTIES HEADER_FILE_ONLY TRUE)
set(GENERATOR_SOURCES src/main.cpp src/builder.cpp src/execution.cpp "${GENERATED_FUNCTION}")
add_executable(app_ir_generator ${GENERATOR_SOURCES} "${APP_SOURCE_DIR}/src/sim.c")
add_dependencies(app_ir_generator app_ir_generator_sources)
set_target_properties(app_ir_generator PROPERTIES
    OUTPUT_NAME ir_generator
    RUNTIME_OUTPUT_DIRECTORY "${PROJECT_BINARY_DIR}"
)

separate_arguments(LLVM_DEFINITION_FLAGS NATIVE_COMMAND "${LLVM_DEFINITIONS}")
target_compile_features(app_ir_generator PRIVATE c_std_11 cxx_std_17)
target_include_directories(app_ir_generator PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}/include" "${CMAKE_CURRENT_BINARY_DIR}" "${APP_SOURCE_DIR}/include")
target_include_directories(app_ir_generator SYSTEM PRIVATE ${LLVM_INCLUDE_DIRS})
target_compile_options(app_ir_generator PRIVATE ${LLVM_DEFINITION_FLAGS} "-I${SDL2_ROOT_INCLUDE_DIR}")
target_link_libraries(app_ir_generator PRIVATE LLVM SDL2::SDL2)
