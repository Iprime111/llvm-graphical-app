#pragma once

#include "llvm/IR/LLVMContext.h"
#include "llvm/IR/Module.h"

#include <memory>

std::unique_ptr<llvm::Module> buildAppModule(llvm::LLVMContext &context);
