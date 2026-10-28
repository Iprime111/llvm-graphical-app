from dataclasses import dataclass, field
from typing import Optional, Union
import re

NAME = r'[-a-zA-Z$._0-9]+'
TYPE = r'(?:void|i1|i32)'
BINARY_OPCODES = {'add', 'sub', 'mul', 'shl', 'lshr', 'and'}
PREDICATES = {'eq', 'ne', 'slt', 'sle', 'sgt', 'sge', 'ult', 'ule', 'ugt', 'uge'}


@dataclass
class ValueReference:
    name: str


@dataclass
class IntegerConstant:
    literal: str


@dataclass
class TypedValue:
    type: str
    operand: Union[ValueReference, IntegerConstant]


@dataclass
class Parameter:
    type: str
    name: str


@dataclass
class Instruction:
    result: str
    opcode: str
    line: int


@dataclass
class BinaryInstruction(Instruction):
    left: TypedValue
    right: TypedValue
    flags: list[str]


@dataclass
class ICmpInstruction(Instruction):
    predicate: str
    left: TypedValue
    right: TypedValue
    samesign: bool


@dataclass
class SelectInstruction(Instruction):
    condition: TypedValue
    yes: TypedValue
    no: TypedValue


@dataclass
class CallInstruction(Instruction):
    target: str
    return_type: str
    arguments: list[TypedValue]
    fastcc: bool
    tail: str


@dataclass
class BranchInstruction(Instruction):
    target: str


@dataclass
class ConditionalBranchInstruction(Instruction):
    condition: TypedValue
    true_target: str
    false_target: str


@dataclass
class ReturnInstruction(Instruction):
    value: Optional[TypedValue]


@dataclass
class PhiIncoming:
    value: TypedValue
    block: str


@dataclass
class PhiInstruction(Instruction):
    type: str
    incoming: list[PhiIncoming]


@dataclass
class BasicBlock:
    name: str
    instructions: list[Instruction] = field(default_factory=list)


@dataclass
class Function:
    name: str
    return_type: str
    parameters: list[Parameter]
    internal: bool
    fastcc: bool
    attribute: str
    blocks: dict[str, BasicBlock] = field(default_factory=dict)


@dataclass
class AttributeGroup:
    number: str
    attributes: list[str]


@dataclass
class Module:
    functions: dict[str, Function] = field(default_factory=dict)
    attributes: dict[str, AttributeGroup] = field(default_factory=dict)

    def reachable_functions(self, entry: str) -> list[Function]:
        """Return functions reachable by direct calls, preserving their input order."""
        functions = self.functions
        if entry not in functions or not functions[entry].blocks:
            raise ValueError(f'entry @{entry} has no definition')
        seen, pending = set(), [entry]
        while pending:
            name = pending.pop()
            if name in seen:
                continue
            if name not in functions:
                raise ValueError(f'undeclared function @{name}')
            seen.add(name)
            for block in functions[name].blocks.values():
                for instruction in block.instructions:
                    if isinstance(instruction, CallInstruction):
                        pending.append(instruction.target)
        return [fn for name, fn in functions.items() if name in seen]


def split_arguments(text):
    """Split commas outside (...) and [...], including range attrs and PHIs."""
    arguments, start, depth = [], 0, 0
    for index, char in enumerate(text):
        if char in '([':
            depth += 1
        elif char in ')]':
            depth -= 1
        elif char == ',' and depth == 0:
            arguments.append(text[start:index].strip())
            start = index + 1
    if depth != 0:
        raise ValueError(f'unbalanced arguments: {text}')
    if text[start:].strip():
        arguments.append(text[start:].strip())
    return arguments


def extract_result(text):
    """Return the result name, or an empty string, and the remaining instruction."""
    match = re.match(rf'^%({NAME})\s*=\s*(.*)$', text)
    return (match[1], match[2]) if match else ('', text)


def extract_opcode(text):
    """Return the opcode, argument text and optional tail-call marker."""
    tail = ''
    if text.startswith(('tail ', 'musttail ', 'notail ')):
        tail, text = text.split(None, 1)
    parts = text.split(None, 1)
    return parts[0], parts[1] if len(parts) == 2 else '', tail


def strip_annotations(text):
    """Remove noundef and integer range annotations ignored by the generator."""
    # These optimizer annotations are intentionally outside the reconstructed IR.
    text = re.sub(r'\brange\(i32 -?\d+, -?\d+\)\s*', '', text)
    return re.sub(r'\bnoundef\s*', '', text)


class IRParser:
    """Parse supported IR text into modules and their extracted entities."""

    @staticmethod
    def parse_typed_value(text: str) -> TypedValue:
        """Extract the type and operand from a supported value such as i32 %x."""
        match = re.fullmatch(rf'(i1|i32)\s+(%{NAME}|-?\d+|true|false)', text.strip())
        if not match:
            raise ValueError(f'unsupported typed value: {text}')
        operand = (ValueReference(match[2][1:]) if match[2].startswith('%') else
                   IntegerConstant({'true': '1', 'false': '0'}.get(match[2], match[2])))
        return TypedValue(type=match[1], operand=operand)

    @staticmethod
    def parse_call(arguments: str, result: str, tail: str, line: int) -> CallInstruction:
        """Extract the direct callee, typed arguments and calling convention."""
        match = re.fullmatch(
            rf'(?:(fastcc)\s+)?({TYPE})\s+@({NAME})\((.*)\)(?:\s+#\d+)?',
            arguments)
        if not match:
            raise ValueError('only direct calls with void/i1/i32 signatures are supported')
        return CallInstruction(result=result, opcode='call', line=line,
                               target=match[3], return_type=match[2],
                               arguments=[IRParser.parse_typed_value(arg)
                                          for arg in split_arguments(match[4])],
                               fastcc=bool(match[1]), tail=tail)

    @staticmethod
    def parse_destination(text: str) -> str:
        """Extract a basic-block name from a branch label operand."""
        if not text.startswith('label %'):
            raise ValueError(f'invalid branch destination: {text}')
        return text[len('label %'):]

    def parse_instruction(self, text: str, line: int) -> Instruction:
        """Extract all opcode-specific fields once, retaining the source line."""
        text = strip_annotations(re.sub(r',\s*!.*$', '', text))
        result, body = extract_result(text)
        opcode, arguments, tail = extract_opcode(body)
        if tail and opcode != 'call':
            raise ValueError('tail marker is only supported on calls')
        fields = dict(result=result, opcode=opcode, line=line)
        if opcode in BINARY_OPCODES:
            tokens = arguments.split()
            flags = []
            while tokens and tokens[0] in ('nuw', 'nsw', 'exact'):
                flags.append(tokens.pop(0))
            ty, operands = ' '.join(tokens).split(None, 1)
            left, right = [self.parse_typed_value(f'{ty} {arg}')
                           for arg in split_arguments(operands)]
            return BinaryInstruction(**fields, left=left, right=right, flags=flags)
        if opcode == 'icmp':
            tokens = arguments.split()
            samesign = tokens[0] == 'samesign'
            if samesign:
                tokens.pop(0)
            predicate, ty = tokens[:2]
            if predicate not in PREDICATES:
                raise ValueError(f'unsupported predicate {predicate}')
            left, right = [self.parse_typed_value(f'{ty} {arg}')
                           for arg in split_arguments(' '.join(tokens[2:]))]
            return ICmpInstruction(**fields, predicate=predicate,
                                   left=left, right=right, samesign=samesign)
        if opcode == 'select':
            condition, yes, no = [self.parse_typed_value(arg) for arg in split_arguments(arguments)]
            return SelectInstruction(**fields, condition=condition, yes=yes, no=no)
        if opcode == 'call':
            return self.parse_call(arguments, result, tail, line)
        if opcode == 'br':
            args = split_arguments(arguments)
            if len(args) == 1:
                return BranchInstruction(**fields, target=self.parse_destination(args[0]))
            return ConditionalBranchInstruction(
                **fields, condition=self.parse_typed_value(args[0]),
                true_target=self.parse_destination(args[1]),
                false_target=self.parse_destination(args[2]))
        if opcode == 'ret':
            value = None if arguments == 'void' else self.parse_typed_value(arguments)
            return ReturnInstruction(**fields, value=value)
        if opcode == 'phi':
            ty, pairs = arguments.split(None, 1)
            incoming = []
            for pair in split_arguments(pairs):
                if not pair.startswith('[') or not pair.endswith(']'):
                    raise ValueError(f'invalid PHI input: {pair}')
                operand, block = split_arguments(pair[1:-1])
                incoming.append(PhiIncoming(self.parse_typed_value(f'{ty} {operand}'),
                                            block.removeprefix('%')))
            return PhiInstruction(**fields, type=ty, incoming=incoming)
        raise ValueError(f'unsupported opcode {opcode}')

    @staticmethod
    def parse_parameters(text: str, definition: bool) -> list[Parameter]:
        """Extract parameter types and names, requiring names in definitions."""
        parameters = []
        for arg in split_arguments(strip_annotations(text)):
            param = re.fullmatch(rf'(i1|i32)(?:\s+%({NAME}))?', arg)
            if not param or (definition and not param[2]):
                raise ValueError(f'unsupported parameter: {arg}')
            parameters.append(Parameter(type=param[1], name=param[2] or ''))
        return parameters

    def parse_function_header(self, line: str) -> tuple[Function, bool]:
        """Extract a function and whether the header starts a definition."""
        header = re.fullmatch(rf'(define|declare) (.*?)@({NAME})\((.*)\)\s*(.*)', line)
        if not header:
            raise ValueError('unsupported function header')
        prefix = header[2].split()
        if not prefix or any(token not in ('internal', 'fastcc', 'dso_local', 'void', 'i1', 'i32')
                             for token in prefix):
            raise ValueError('unsupported function signature')
        definition = header[1] == 'define'
        if definition and not header[5].endswith('{'):
            raise ValueError('expected function body on following lines')
        attribute = re.search(r'#(\d+)', header[5])
        function = Function(name=header[3], return_type=prefix[-1],
                            parameters=self.parse_parameters(header[4], definition),
                            internal='internal' in prefix, fastcc='fastcc' in prefix,
                            attribute=attribute[1] if attribute else '')
        return function, definition

    def parse_body_line(self, function: Function, block: Optional[BasicBlock],
                        line: str, number: int) -> BasicBlock:
        """Record a block label or instruction and return the current block."""
        if re.fullmatch(rf'{NAME}:', line):
            name = line[:-1]
            if name in function.blocks:
                raise ValueError(f'duplicate block {name}')
            block = BasicBlock(name=name)
            function.blocks[name] = block
            return block
        if block is None:
            raise ValueError('expected an explicit basic block label')
        block.instructions.append(self.parse_instruction(line, number))
        return block

    def parse_module_statement(self, module: Module, line: str) -> Optional[Function]:
        """Read declarations and attributes, skipping source and target information."""
        if line.startswith(('source_filename = ', 'target triple = ', 'target datalayout = ')):
            return None
        if line.startswith(('define ', 'declare ')):
            function, definition = self.parse_function_header(line)
            if function.name in module.functions:
                raise ValueError('duplicate function')
            module.functions[function.name] = function
            return function if definition else None
        if line.startswith('attributes #'):
            attribute = re.fullmatch(r'attributes #(\d+) = \{(.*)\}', line)
            if not attribute:
                raise ValueError('unsupported attribute group')
            module.attributes[attribute[1]] = AttributeGroup(
                number=attribute[1], attributes=attribute[2].split())
            return None
        if not line.startswith('!'):
            raise ValueError(f'unsupported module statement: {line}')
        return None

    def parse_module(self, text: str) -> Module:
        """Collect functions, blocks, instructions and attributes from IR text."""
        module = Module()
        function, block = None, None
        for number, raw_line in enumerate(text.splitlines(), 1):
            line = raw_line.split(';', 1)[0].strip()
            if not line:
                continue
            try:
                if function is None:
                    function = self.parse_module_statement(module, line)
                    block = None
                elif line == '}':
                    function = None
                else:
                    block = self.parse_body_line(function, block, line, number)
            except ValueError as error:
                raise ValueError(f'line {number}: {error}') from error
        if function is not None:
            raise ValueError('unterminated function body')
        return module
