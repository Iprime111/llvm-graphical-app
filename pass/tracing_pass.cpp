#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/Module.h"
#include "llvm/IR/PassManager.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/ErrorHandling.h"
#include "llvm/Support/FileSystem.h"
#include "llvm/Support/raw_ostream.h"

#include <cstddef>

namespace {

class BlockIdGenerator {
public:
    std::size_t getNextId()
    {
        return nextId++;
    }

private:
    std::size_t nextId = 0;
};

class TracingPassImpl {
public:
    explicit TracingPassImpl(llvm::Module &module)
        : module(module), builder(module.getContext()),
          blockIdType(builder.getIntPtrTy(module.getDataLayout())),
          traceType(llvm::FunctionType::get(builder.getVoidTy(), {blockIdType}, false)),
          metadata(MetadataFileName, error, llvm::sys::fs::OF_Text)
    {
        if (error) {
            llvm::report_fatal_error(llvm::Twine("Cannot create ") + MetadataFileName + ": " +
                                    error.message());
        }
    }

    bool run()
    {
        bool changed = traceModule();
        metadata.flush();
        if (metadata.has_error()) {
            llvm::report_fatal_error(llvm::Twine("Cannot write ") + MetadataFileName);
        }
        return changed;
    }

private:
    static constexpr char TraceFunctionName[] = "writeBbNumber";
    static constexpr char MetadataFileName[] = "bb_metadata.txt";

    void processPhiOperand(llvm::Instruction &user, llvm::PHINode &phi)
    {
        for (auto &incoming : phi.incoming_values()) {
            if (auto *instruction = llvm::dyn_cast<llvm::Instruction>(incoming.get())) {
                metadata << user.getOpcodeName() << " <- "
                         << instruction->getOpcodeName() << '\n';
            }
        }
    }

    void writeBlockMetadata(llvm::BasicBlock &block, std::size_t blockId)
    {
        metadata << "BB" << blockId << ":\n";
        for (auto &user : block) {
            if (llvm::isa<llvm::PHINode>(user)) {
                continue;
            }
            
            for (auto &operand : user.operands()) {
                if (auto *phi = llvm::dyn_cast<llvm::PHINode>(operand.get())) {
                    processPhiOperand(user, *phi);
                    continue;
                }
                
                if (auto *instruction = llvm::dyn_cast<llvm::Instruction>(operand.get())) {
                    metadata << user.getOpcodeName() << " <- "
                             << instruction->getOpcodeName() << '\n';
                }
            }
        }
    }

    void instrumentBlock(llvm::BasicBlock &block, std::size_t blockId)
    {
        auto insertionPoint = block.getFirstInsertionPt();
        if (insertionPoint == block.end()) {
            llvm::report_fatal_error("No legal insertion point for BB tracing");
        }

        builder.SetInsertPoint(&block, insertionPoint);
        builder.CreateCall(traceFunction, {llvm::ConstantInt::get(blockIdType, blockId)});
    }

    bool traceModule()
    {
        for (auto &function : module) {
            if (function.empty() || function.getName() == TraceFunctionName) {
                continue;
            }
            
            if (traceFunction.getCallee() == nullptr) {
                traceFunction = module.getOrInsertFunction(TraceFunctionName, traceType);
            }
            
            for (auto &block : function) {
                auto blockId = blockIds.getNextId();
                writeBlockMetadata(block, blockId);
                instrumentBlock(block, blockId);
            }
        }
        return traceFunction.getCallee() != nullptr;
    }

    llvm::Module &module;
    llvm::IRBuilder<> builder;
    llvm::IntegerType *blockIdType;
    llvm::FunctionType *traceType;
    llvm::FunctionCallee traceFunction;
    BlockIdGenerator blockIds;
    std::error_code error;
    llvm::raw_fd_ostream metadata;
};

class TracingPass : public llvm::PassInfoMixin<TracingPass> {
public:
    llvm::PreservedAnalyses run(llvm::Module &module, llvm::ModuleAnalysisManager &)
    {
        bool changed = TracingPassImpl(module).run();
        return changed ? llvm::PreservedAnalyses::none() : llvm::PreservedAnalyses::all();
    }

    static bool isRequired() { return true; }
};
} // namespace

extern "C" LLVM_ATTRIBUTE_WEAK llvm::PassPluginLibraryInfo llvmGetPassPluginInfo()
{
    return {LLVM_PLUGIN_API_VERSION, "TracingPass", LLVM_VERSION_STRING,
            [](llvm::PassBuilder &builder) {
                builder.registerOptimizerLastEPCallback(
                    [](llvm::ModulePassManager &manager, llvm::OptimizationLevel,
                       llvm::ThinOrFullLTOPhase) {
                        manager.addPass(TracingPass());
                    });
            }};
}
