# Exterminatus

A small C and SDL2 animation of Exterminatus from Warhammer 40,000, made for the LLVM course. A warship fires at a planet, producing a growing fireball and smoke. The build also generates `app/app.ll` from `app/src/app.c` for inspecting the LLVM IR.

## Table of contents

- [Trace pass results](#trace-pass-results)
- [LLVM IR generator](#llvm-ir-generator)
- [Build with Nix](#build-with-nix)
- [Build without Nix](#build-without-nix)

## LLVM IR generator

See [LLVM IR generator README](ir_generator/README.md) for the generation pipeline
and build/run instructions.

## Trace pass results

See [Trace pass results and script guides](docs/patterns.md) for result charts,
trace and metadata formats, and instructions for running the analysis scripts.

![A warship unleashing Exterminatus on a planet](docs/app.png)

## Build with Nix

From the project directory:

```sh
nix develop
cmake -S . -B build -G Ninja
cmake --build build
./build/graphical_app
```

The flake provides matching Clang and LLVM 21 dependencies, plus Python with
Matplotlib for trace statistics. The build also
creates `graphical_app_traced`, compiling only `app/src/app.c` with the pass
plugin in `pass/`. Both executables and the pass plugin compile with `-Os`,
as does the generated LLVM IR.

To build and run that target separately:

```sh
cmake --build build --target graphical_app_traced
./build/graphical_app_traced
```

`nix build` installs both executables in `result/bin/`.

## Build without Nix

Install matching versions of Clang and LLVM (including development headers),
CMake, Ninja, and SDL2, then run:

```sh
cmake -S . -B build -G Ninja -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++
cmake --build build
./build/graphical_app
```

Close the window to exit.
