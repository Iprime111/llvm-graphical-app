include_guard(GLOBAL)

get_filename_component(APP_SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}/../app" ABSOLUTE)

if(CMAKE_C_COMPILER_ID MATCHES "Clang")
    set(APP_IR_CLANG "${CMAKE_C_COMPILER}")
else()
    find_program(APP_IR_CLANG NAMES clang REQUIRED)
endif()

set(APP_IR_FILE "${APP_SOURCE_DIR}/app.ll")
add_custom_command(
    OUTPUT "${APP_IR_FILE}"
    COMMAND "${APP_IR_CLANG}" -std=c11 -Os -S -emit-llvm
            -fno-discard-value-names
            "-I${APP_SOURCE_DIR}/include"
            "${APP_SOURCE_DIR}/src/app.c"
            -o "${APP_IR_FILE}"
    DEPENDS "${APP_SOURCE_DIR}/src/app.c" "${APP_SOURCE_DIR}/include/sim.h"
    COMMENT "Generating LLVM IR for app.c"
    VERBATIM
)
add_custom_target(app_ir ALL DEPENDS "${APP_IR_FILE}")
