from xdsl.context import Context
from xdsl.parser import Parser
from xdsl.dialects.builtin import Builtin, IntegerAttr
from xdsl.dialects.llvm import LLVM, StoreOp, AllocaOp, ConstantOp, AddOp, LoadOp
from xdsl.dialects.dlti import DLTI
from xdsl.dialects.riscv import RISCV
from xdsl.printer import Printer
# PatternRewriter used for converting MLIR to the RISCV dialect
from xdsl.pattern_rewriter import PatternRewriteWalker, GreedyRewritePatternApplier

from xdsl_riscv_lowering import LowerLLVMAddToRISCV, LowerLLVMConstantToRISCV

# If you add new microC codes please replace this name
MICROC_CODE = "microc_1.mlir"

# LLVM uses virtual mmeory variables
# but RISCV needs physical stack slots
alloca_map = {}
stack_offset = 0

# Mapping allocations to RISCV registers
reg_names = ['t0', 't1', 't2', 't3', 't4', 't5', 't6', 't7', 't8', 't9', 't10']
reg_index = 0
value_reg_map = {}

def alloc_reg():
    global reg_index
    r = reg_names[reg_index]
    reg_index += 1
    return r

ctx = Context()
# Load all these following dialects
ctx.load_dialect(Builtin)
ctx.load_dialect(LLVM)
ctx.load_dialect(DLTI)
ctx.load_dialect(RISCV)

printer = Printer()

with open(f"./sample_codes/{MICROC_CODE}", "r") as f:
    parser = Parser(ctx, f.read())
    module = parser.parse_module()

print("Successfully loaded MLIR into xDSL!")

# patterns = GreedyRewritePatternApplier([
#     LowerLLVMConstantToRISCV(),
#     LowerLLVMAddToRISCV(),
# ])

# walker = PatternRewriteWalker(patterns)
# walker.rewrite_module(module)

# Walk through all ops and find llvm.alloca
for op in module.walk():
    if isinstance(op, AllocaOp):
        result = op.results[0]
        alloca_map[result] = stack_offset
        stack_offset += 4

# Walk through all ops and find llvm.constant
for op in module.walk():
    if isinstance(op, ConstantOp):
        reg = alloc_reg()
        value_reg_map[op.results[0]] = reg
        print(f'li {reg}, {op.value.value.data}')

store_operands = []
load_results = []
load_operands = []

for op in module.walk():
    if isinstance(op, StoreOp):
        store_operands.append(op)

for op in module.walk():
    new_map = {}
    if isinstance(op, LoadOp):
        for sop in store_operands:
            if op.operands[0] == sop.operands[1]:
                for k, v in value_reg_map.items():
                    if sop.operands[0] == k:
                        new_map[op.results[0]] = v
        value_reg_map.update(new_map)
        # reg = alloc_reg()
        # value_reg_map[op.results[0]] = reg
        # offset = alloca_map[op.operands[0]]
        # print(f'lw {reg}, {offset}(sp)')

# Walk through all ops and find llvm.add
for op in module.walk():
    if isinstance(op, AddOp):
        r1 = value_reg_map[op.lhs]
        r2 = value_reg_map[op.rhs]
        rout = alloc_reg()
        value_reg_map[op.results[0]] = rout

        print(f'add {rout}, {r1}, {r2}')