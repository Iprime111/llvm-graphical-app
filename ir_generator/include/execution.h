#pragma once

#include "llvm/IR/Module.h"

#include <memory>

int runApp(std::unique_ptr<llvm::Module> module);
