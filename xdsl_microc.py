from xdsl.context import Context
from xdsl.parser import Parser
from xdsl.dialects.builtin import Builtin
from xdsl.dialects.llvm import LLVM
from xdsl.dialects.dlti import DLTI
from xdsl.dialects.riscv import RISCV
from xdsl.printer import Printer
# PatternRewriter used for converting MLIR to the RISCV dialect
from xdsl.pattern_rewriter import PatternRewriteWalker, GreedyRewritePatternApplier

from xdsl_riscv_lowering import LowerLLVMToRISCV

# If you add new microC codes please replace this name
MICROC_CODE = "microc_1.mlir"

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

# Uncomment if you want to see the end result
# for op in module.walk():
#     print(f'found op with name {op.name}')

patterns = GreedyRewritePatternApplier([
    LowerLLVMToRISCV(),
])

walker = PatternRewriteWalker(patterns)
walker.rewrite_module(module)

for op in module.walk():
    print(f'{op}')