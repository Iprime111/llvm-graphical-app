# LLVM IR generator

The generator rebuilds the application's LLVM IR using C++ `IRBuilder` calls,
then verifies and JIT-executes the resulting module or writes it to a file.

```text
app/src/app.c → app/app.ll → Python generator → app_builder.inc
                                                    ↓
                                                LLVM Module → JIT / rebuilt.ll
```

From the repository root, with LLVM 21, SDL2 and Python 3.9+ available:

```sh
nix develop  # Provides the dependencies.
cmake -S . -B build -G Ninja
cmake --build build --target app_ir_generator
./build/ir_generator                   # Run the animation.
./build/ir_generator build/rebuilt.ll  # Write IR without opening a window.
```

CMake regenerates the C++ when the input IR or Python scripts change. To run
only the Python stage after configuring the build:

```sh
python3 ir_generator/scripts/generate.py app/app.ll -o build/ir_generator_build/app_builder.inc
```

