# Exterminatus

A small C and SDL2 animation of Exterminatus from Warhammer 40,000, made for the LLVM course. A warship fires at a planet, producing a growing fireball and smoke. The build also generates `app.ll` from `src/app.c` for inspecting the LLVM IR.

![A warship unleashing Exterminatus on a planet](docs/app.png)

## Build with Nix

From the project directory:

```sh
nix develop
cmake -S . -B build -G Ninja
cmake --build build
./build/graphical_app
```

## Build without Nix

Install Clang, CMake, Ninja, and SDL2, then run:

```sh
cmake -S . -B build -G Ninja
cmake --build build
./build/graphical_app
```

Close the window to exit.

## Generated LLVM IR

Every build also generates `app.ll` from `src/app.c`. The `app_ir` target can regenerate it on its own:

```sh
cmake --build build --target app_ir
```

The IR command uses `-std=c11` for C11, `-Os` to optimize for size, and `-S -emit-llvm` to write readable `.ll` text. `-fno-discard-value-names` retains names such as `%radius` where possible, making the IR easier to inspect. It also adds the project's `include/` directory for `sim.h`.

When the configured C compiler is Clang, CMake uses that same compiler to generate the IR. To choose a different Clang, configure a fresh build directory with `CMAKE_C_COMPILER` (this also changes the compiler used for the executable):

```sh
cmake -S . -B build-clang -G Ninja -DCMAKE_C_COMPILER=/absolute/path/to/clang
cmake --build build-clang --target app_ir
```

If the configured C compiler is not Clang, CMake looks for `clang` on `PATH` for IR generation. In that case, `-DAPP_IR_CLANG=/absolute/path/to/clang` can select a specific Clang for the IR target.
