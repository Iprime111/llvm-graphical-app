cmake_minimum_required(VERSION 3.20)
project(graphical_app LANGUAGES C CXX)

find_package(SDL2 REQUIRED CONFIG)
find_path(SDL2_ROOT_INCLUDE_DIR NAMES SDL2/SDL.h REQUIRED)

set(APP_SOURCES
    "${CMAKE_CURRENT_SOURCE_DIR}/app/src/app.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/app/src/sim.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/app/src/start.c"
)
add_executable(graphical_app ${APP_SOURCES})
add_subdirectory(pass)

foreach(APP_TARGET IN ITEMS graphical_app graphical_app_traced)
    target_compile_features(${APP_TARGET} PRIVATE c_std_11)
    target_include_directories(${APP_TARGET} PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/app/include")
    target_link_libraries(${APP_TARGET} PRIVATE SDL2::SDL2)
    # Keep Nix's implicit SDL include path visible in compile_commands.json.
    target_compile_options(${APP_TARGET} PRIVATE "-I${SDL2_ROOT_INCLUDE_DIR}" -Wall -Os)
endforeach()

include(cmake/AppIR.cmake)
add_subdirectory(ir_generator ir_generator_build)

install(TARGETS graphical_app graphical_app_traced RUNTIME DESTINATION bin)
