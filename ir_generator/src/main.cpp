#include "generator.h"
#include "execution.h"

#include "llvm/IR/Verifier.h"
#include "llvm/Support/FileSystem.h"
#include "llvm/Support/raw_ostream.h"

int main(int argc, char **argv)
{
    if (argc > 2) {
        llvm::errs() << "usage: ir_generator [output.ll]\n"
                     << "Without an output file, run app() through ExecutionEngine.\n";
        return 1;
    }

    llvm::LLVMContext context;
    auto module = buildAppModule(context);
    if (llvm::verifyModule(*module, &llvm::errs())) {
        return 1;
    }

    if (argc == 1) {
        return runApp(std::move(module));
    }

    std::error_code error;
    llvm::raw_fd_ostream output(argv[1], error, llvm::sys::fs::OF_Text);
    if (error) {
        llvm::errs() << error.message() << '\n';
        return 1;
    }
    
    module->print(output, nullptr);
    output.close();
    if (output.has_error()) {
        llvm::errs() << "failed to write IR\n";
        return 1;
    }
}
