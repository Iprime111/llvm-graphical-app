# Exterminatus

A small C and SDL2 animation of Exterminatus from Warhammer 40,000, made for the LLVM course. A warship fires at a planet, producing a growing fireball and smoke. The build also generates `app.ll` from `src/app.c` for inspecting the LLVM IR.

## Table of contents

- [Trace pass results](#trace-pass-results)
- [Build with Nix](#build-with-nix)
- [Build without Nix](#build-without-nix)
- [LLVM tracing pass](#llvm-tracing-pass)
- [Generated LLVM IR](#generated-llvm-ir)

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
creates `graphical_app_traced`, compiling only `src/app.c` with the pass
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

## LLVM tracing pass

`TracingPass` uses LLVM's new pass manager. Clang loads it with
`-fpass-plugin` when compiling `src/app.c` for the traced executable. It runs at
the optimizer-last extension point, at the end of the function optimization
pipeline, before final module cleanup and code generation. At `-O0` it still
runs, but the IR is unoptimized.
Changing the plugin rebuilds only the traced `app.c` object.

`BlockIdGenerator::getNextId()` assigns consecutive IDs across the module,
starting at zero. The pass inserts `writeBbNumber(size_t)` at the start of each
block, after PHI nodes. The runtime in `pass/trace.c` prints one numeric block ID per line and is
compiled without the plugin and linked into `graphical_app_traced`. During
compilation it overwrites `bb_metadata.txt` in the compiler's working directory
(`build/` for the CMake build). Each `BB<number>:` section lists one
`user_opcode <- operand_opcode` line per instruction operand. PHI users and
operands that are not instructions are skipped; PHI operands are included.
Each block's metadata is collected before inserting its trace, in a single
traversal of the module's blocks. The plugin registers an optimizer-last callback;
it does not register a named `tracing` pipeline for `opt -passes=tracing`.

Capture and expand a trace into the metadata instruction lines in execution order:

```sh
./build/graphical_app_traced > trace.txt
python3 scripts/expand_trace.py --trace trace.txt --bb-metadata build/bb_metadata.txt -o trace_expanded.txt
```

Both input paths must be named with `--trace` (`-t`) and `--bb-metadata` (`-m`),
and `-o` is required. This writes the specified output file without block headers.
Repeated blocks repeat their instruction lines; empty blocks contribute no lines.
The output contains only the instruction
operand relationships recorded by the pass.

Collect pattern statistics directly from the block trace, without expanding it:

```sh
nix develop
./build/graphical_app_traced > trace.txt
python3 scripts/trace_stats.py --trace trace.txt --bb-metadata build/bb_metadata.txt -o trace_stats -k 10
```

Close the app window to finish capturing `trace.txt` before collecting statistics.

The named input paths and `-o` output directory are required. This creates
`trace_stats/images/patterns_1.png` through `patterns_5.png`, rendered using
Matplotlib without a GUI. Each column chart shows up to K most frequent retained patterns
of exactly that length, with column heights equal to occurrence counts. The
matching files in `trace_stats/csv/` contain all retained patterns and their counts,
sorted by decreasing frequency (ties use alphabetical pattern order).
The script needs Python 3.9 or newer and Matplotlib, both provided by `nix develop`.
Outside Nix, install Matplotlib in a Python virtual environment.

A pattern is a consecutive sequence of metadata lines (`user <- operand`),
including sequences crossing block boundaries. Occurrences can overlap; empty
blocks contribute no lines and do not break a sequence. A shorter pattern is
filtered out if a longer left or right extension has the same occurrence count.
For example, two-line subsequences occurring only within an equally frequent
four-line pattern are omitted from the length-2 chart. A two-line pattern with
additional independent occurrences is retained. Length-6 extensions are counted
to apply this rule to length 5; they are not charted. If no patterns survive at
a length, its chart displays an empty-state message.

The script aggregates block visits and repeated boundary contexts, then weights
their patterns by occurrence count. Each distinct context is processed once per
batch, instead of recomputing its windows on every visit. Boundary batches are
limited to 50,000 contexts to bound additional memory. Counts and filtering remain
exact, without storing the full executed instruction stream.

## Generated LLVM IR

Every build also generates `app.ll` from `src/app.c`. The `app_ir` target can regenerate it on its own:

```sh
cmake --build build --target app_ir
```

The IR command uses `-std=c11` for C11, `-Os` to optimize for size, and `-S -emit-llvm` to write readable `.ll` text. `-fno-discard-value-names` retains names such as `%radius` where possible, making the IR easier to inspect. It also adds the project's `include/` directory for `sim.h`.

CMake uses the configured Clang compiler to generate the IR. To choose a different Clang, configure a fresh build directory with matching C and C++ compilers and an LLVM installation of the same major version:

```sh
cmake -S . -B build-clang -G Ninja -DCMAKE_C_COMPILER=/absolute/path/to/clang -DCMAKE_CXX_COMPILER=/absolute/path/to/clang++ -DLLVM_DIR=/absolute/path/to/llvm/lib/cmake/llvm
cmake --build build-clang --target app_ir
```
