#include "execution.h"
#include "sim.h"

#include "llvm/ADT/StringRef.h"
#include "llvm/ExecutionEngine/GenericValue.h"
#include "llvm/ExecutionEngine/MCJIT.h"
#include "llvm/Support/TargetSelect.h"
#include "llvm/Support/raw_ostream.h"

#include <unordered_map>
#include <string>

static void *lazyFunctionCreator(llvm::StringRef name)
{
    // Mach-O prefixes external symbol names with an underscore.
    name.consume_front("_");
    static const std::unordered_map<std::string, void *> functions = {
        {"simInit", reinterpret_cast<void *>(&simInit)},
        {"simExit", reinterpret_cast<void *>(&simExit)},
        {"simFlush", reinterpret_cast<void *>(&simFlush)},
        {"simPutPixel", reinterpret_cast<void *>(&simPutPixel)},
        {"simRand", reinterpret_cast<void *>(&simRand)},
        {"simHasClick", reinterpret_cast<void *>(&simHasClick)},
        {"simGetClick", reinterpret_cast<void *>(&simGetClick)},
    };
    
    auto function = functions.find(name.str());
    return function == functions.end() ? nullptr : function->second;
}

int runApp(std::unique_ptr<llvm::Module> module)
{
    if (llvm::InitializeNativeTarget() || llvm::InitializeNativeTargetAsmPrinter()) {
        llvm::errs() << "Cannot initialize the native LLVM target\n";
        return 1;
    }

    auto *ir = module.get();
    std::string error;
    std::unique_ptr<llvm::ExecutionEngine> engine{
        llvm::EngineBuilder(std::move(module))
            .setErrorStr(&error)
            .create()
    };
    
    if (!engine) {
        llvm::errs() << "Cannot create ExecutionEngine: " << error << '\n';
        return 1;
    }

    engine->InstallLazyFunctionCreator(lazyFunctionCreator);
    
    auto *app = ir->getFunction("app");
    if (!app || app->isDeclaration()) {
        llvm::errs() << "Cannot find app() definition\n";
        return 1;
    }
    
    engine->finalizeObject();
    if (engine->hasError()) {
        llvm::errs() << "Cannot compile app(): " << engine->getErrorMessage() << '\n';
        return 1;
    }

    simInit();
    engine->runFunction(app, {});
    simExit();
    
    return 0;
}
