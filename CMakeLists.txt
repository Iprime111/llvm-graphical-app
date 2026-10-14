cmake_minimum_required(VERSION 3.20)
project(graphical_app LANGUAGES C CXX)

find_package(SDL2 REQUIRED CONFIG)
find_path(SDL2_ROOT_INCLUDE_DIR NAMES SDL2/SDL.h REQUIRED)

set(APP_SOURCES
    "${CMAKE_CURRENT_SOURCE_DIR}/src/app.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/src/sim.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/src/start.c"
)
add_executable(graphical_app ${APP_SOURCES})
add_subdirectory(pass)

foreach(APP_TARGET IN ITEMS graphical_app graphical_app_traced)
    target_compile_features(${APP_TARGET} PRIVATE c_std_11)
    target_include_directories(${APP_TARGET} PRIVATE include)
    target_link_libraries(${APP_TARGET} PRIVATE SDL2::SDL2)
    # Keep Nix's implicit SDL include path visible in compile_commands.json.
    target_compile_options(${APP_TARGET} PRIVATE "-I${SDL2_ROOT_INCLUDE_DIR}" -Wall -Os)
endforeach()

if(CMAKE_C_COMPILER_ID MATCHES "Clang")
    set(APP_IR_CLANG "${CMAKE_C_COMPILER}")
else()
    find_program(APP_IR_CLANG NAMES clang REQUIRED)
endif()

set(APP_IR_FILE "${CMAKE_CURRENT_SOURCE_DIR}/app.ll")
add_custom_command(
    OUTPUT "${APP_IR_FILE}"
    COMMAND "${APP_IR_CLANG}" -std=c11 -Os -S -emit-llvm
            -fno-discard-value-names
            "-I${CMAKE_CURRENT_SOURCE_DIR}/include"
            "${CMAKE_CURRENT_SOURCE_DIR}/src/app.c"
            -o "${APP_IR_FILE}"
    DEPENDS src/app.c include/sim.h
    COMMENT "Generating LLVM IR for app.c"
    VERBATIM
)
add_custom_target(app_ir ALL DEPENDS "${APP_IR_FILE}")

install(TARGETS graphical_app graphical_app_traced RUNTIME DESTINATION bin)
