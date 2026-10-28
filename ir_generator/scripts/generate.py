import argparse
import json
from pathlib import Path

from ir_parser import (BinaryInstruction, BranchInstruction, CallInstruction,
                       ConditionalBranchInstruction, ICmpInstruction, IRParser,
                       PhiInstruction, ReturnInstruction, SelectInstruction, ValueReference)

BINARY = {'add': 'Add', 'sub': 'Sub', 'mul': 'Mul', 'shl': 'Shl', 'lshr': 'LShr', 'and': 'And'}
TYPES = {'void': 'Type::getVoidTy(context)', 'i1': 'Type::getInt1Ty(context)',
         'i32': 'Type::getInt32Ty(context)'}


def generate_cpp(text, entry='app'):
    module = IRParser().parse_module(text)
    functions = module.reachable_functions(entry)
    function_refs = {fn.name: f'fn{index}' for index, fn in enumerate(functions)}
    lines = ['std::unique_ptr<Module> buildAppModule(LLVMContext &context)', '{']
    indent = 1

    def emit(line):
        nonlocal indent
        if line == '}':
            indent -= 1
        lines.append('    ' * indent + line)
        if line == '{':
            indent += 1

    emit_module_setup(emit)
    emit_function_declarations(functions, module.attributes, function_refs, emit)
    for fn in functions:
        if fn.blocks:
            emit_body(fn, function_refs, emit)
    emit('return module;')
    return '\n'.join(lines + ['}']) + '\n'


def emit_module_setup(emit):
    emit('auto module = std::make_unique<Module>("app.c", context);')
    emit('IRBuilder<NoFolder> builder(context);')


def emit_function_declarations(functions, attributes, function_refs, emit):
    """Emit function signatures, linkage and supported function attributes."""
    for fn in functions:
        reference = function_refs[fn.name]
        parameters = ', '.join(TYPES[param.type] for param in fn.parameters)
        linkage = 'InternalLinkage' if fn.internal else 'ExternalLinkage'
        emit(f'auto *{reference} = Function::Create(FunctionType::get({TYPES[fn.return_type]}, {{{parameters}}}, false),')
        emit(f'    GlobalValue::{linkage}, {json.dumps(fn.name)}, *module);')
        if fn.fastcc:
            emit(f'{reference}->setCallingConv(CallingConv::Fast);')
        attribute = attributes.get(fn.attribute)
        if attribute and 'noinline' in attribute.attributes:
            emit(f'{reference}->addFnAttr(Attribute::NoInline);')


def emit_body(function, function_refs, emit):
    """Declare blocks/PHIs first; connect loop backedges after the body exists."""
    emit('{')
    reference = function_refs[function.name]
    values = {}
    blocks = {name: f'bb{index}' for index, name in enumerate(function.blocks)}
    for index, parameter in enumerate(function.parameters):
        name = parameter.name
        values[name] = f'{reference}->getArg({index})'
        emit(f'{values[name]}->setName({json.dumps(name)});')
    for name, block in blocks.items():
        emit(f'auto *{block} = BasicBlock::Create(context, {json.dumps(name)}, {reference});')
    phis = []
    for block, basic_block in function.blocks.items():
        for instruction in basic_block.instructions:
            if isinstance(instruction, PhiInstruction):
                name = instruction.result
                values[name] = f'phi{len(phis)}'
                emit(f'builder.SetInsertPoint({blocks[block]});')
                emit(f'auto *{values[name]} = builder.CreatePHI({TYPES[instruction.type]}, {len(instruction.incoming)}, {llvm_name(name)});')
                phis.append(instruction)

    def value(typed_value):
        """Resolve an SSA reference or emit an already parsed integer constant."""
        operand = typed_value.operand
        if isinstance(operand, ValueReference):
            if operand.name not in values:
                raise ValueError(f'unknown or forward value %{operand.name}; only PHI backedges are supported')
            return values[operand.name]
        return f'ConstantInt::get({TYPES[typed_value.type]}, {operand.literal})'

    counter = 0
    for block, basic_block in function.blocks.items():
        emit(f'builder.SetInsertPoint({blocks[block]});')
        for instruction in basic_block.instructions:
            if isinstance(instruction, PhiInstruction):
                continue
            result = f'v{counter}'
            counter += 1
            try:
                emit_instruction(instruction, result, blocks, function_refs, value, emit)
            except (ValueError, KeyError) as error:
                raise ValueError(f'line {instruction.line}: {error}') from error
            if instruction.result:
                values[instruction.result] = result
    for phi in phis:
        for incoming in phi.incoming:
            try:
                emit(f'{values[phi.result]}->addIncoming({value(incoming.value)}, {blocks[incoming.block]});')
            except (ValueError, KeyError) as error:
                raise ValueError(f'line {phi.line}: {error}') from error
    emit('}')


def llvm_name(name):
    """Quote a named LLVM value, using an empty name for numeric SSA slots."""
    return json.dumps('' if name.isdigit() else name)


def emit_instruction(instruction, result, blocks, functions, value, emit):
    """Emit an IRBuilder call from fully parsed instruction fields."""
    name = llvm_name(instruction.result)
    if isinstance(instruction, BinaryInstruction):
        left, right = value(instruction.left), value(instruction.right)
        expression = f'builder.Create{BINARY[instruction.opcode]}({left}, {right}, {name})'
    elif isinstance(instruction, ICmpInstruction):
        left, right = value(instruction.left), value(instruction.right)
        expression = f'builder.CreateICmp(CmpInst::ICMP_{instruction.predicate.upper()}, {left}, {right}, {name})'
    elif isinstance(instruction, SelectInstruction):
        condition, yes, no = value(instruction.condition), value(instruction.yes), value(instruction.no)
        expression = f'builder.CreateSelect({condition}, {yes}, {no}, {name})'
    elif isinstance(instruction, CallInstruction):
        operands = ', '.join(value(arg) for arg in instruction.arguments)
        expression = f'builder.CreateCall({functions[instruction.target]}, {{{operands}}}, {name})'
    elif isinstance(instruction, BranchInstruction):
        expression = f'builder.CreateBr({blocks[instruction.target]})'
    elif isinstance(instruction, ConditionalBranchInstruction):
        expression = f'builder.CreateCondBr({value(instruction.condition)}, {blocks[instruction.true_target]}, {blocks[instruction.false_target]})'
    elif isinstance(instruction, ReturnInstruction):
        expression = ('builder.CreateRetVoid()' if instruction.value is None else
                      f'builder.CreateRet({value(instruction.value)})')
    else:
        raise ValueError(f'unsupported opcode {instruction.opcode}')
    emit(f'auto *{result} = {expression};')
    if isinstance(instruction, BinaryInstruction):
        for flag, setter in [('nuw', 'setHasNoUnsignedWrap'), ('nsw', 'setHasNoSignedWrap'), ('exact', 'setIsExact')]:
            if flag in instruction.flags:
                emit(f'cast<BinaryOperator>({result})->{setter}(true);')
    if isinstance(instruction, ICmpInstruction) and instruction.samesign:
        emit(f'cast<ICmpInst>({result})->setSameSign(true);')
    if isinstance(instruction, CallInstruction):
        if instruction.fastcc:
            emit(f'{result}->setCallingConv(CallingConv::Fast);')
        if instruction.tail:
            kind = {'tail': 'Tail', 'musttail': 'MustTail', 'notail': 'NoTail'}[instruction.tail]
            emit(f'{result}->setTailCallKind(CallInst::TCK_{kind});')


def main():
    """Read the input IR and write the generated C++ function to the output path."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('-o', '--output', type=Path, required=True)
    parser.add_argument('--entry', default='app')
    args = parser.parse_args()
    try:
        source = generate_cpp(args.input.read_text(), args.entry)
        args.output.write_text(source)
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f'error: {error}\n')


if __name__ == '__main__':
    main()
