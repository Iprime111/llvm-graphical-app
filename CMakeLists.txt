cmake_minimum_required(VERSION 3.20)
project(graphical_app LANGUAGES C)

find_package(SDL2 REQUIRED CONFIG)
find_path(SDL2_ROOT_INCLUDE_DIR NAMES SDL2/SDL.h REQUIRED)

add_executable(graphical_app
    src/app.c
    src/sim.c
    src/start.c
)

target_compile_features(graphical_app PRIVATE c_std_11)
target_include_directories(graphical_app PRIVATE include)
target_link_libraries(graphical_app PRIVATE SDL2::SDL2)

# Nix's compiler wrapper adds this directory implicitly, so CMake otherwise
# omits it from compile_commands.json.
target_compile_options(graphical_app PRIVATE "-I${SDL2_ROOT_INCLUDE_DIR}")

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

install(TARGETS graphical_app RUNTIME DESTINATION bin)

target_compile_options(graphical_app PRIVATE -Wall)
