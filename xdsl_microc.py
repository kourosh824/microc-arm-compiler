from xdsl.context import Context
from xdsl.parser import Parser
from xdsl.dialects.builtin import Builtin
from xdsl.dialects.llvm import LLVM
from xdsl.dialects.dlti import DLTI
from xdsl.printer import Printer

from xdsl_arm_backend import ARMBackend
from xdsl_llvm_operations import BrOp, CondBrOp

# If you add new microC codes please replace this name
MICROC_CODE = "microc_3.mlir"

ctx = Context()
# Load all these following dialects
ctx.load_dialect(Builtin)
ctx.load_dialect(LLVM)
ctx.load_dialect(DLTI)

# Loading new LLVM operations
ctx.load_op(BrOp)
ctx.load_op(CondBrOp)

printer = Printer()

with open(f"./sample_codes/{MICROC_CODE}", "r") as f:
    parser = Parser(ctx, f.read())
    module = parser.parse_module()

print("Successfully loaded MLIR into xDSL!")
arm = ARMBackend(module)
arm.walk()
arm.save_code('./sample_codes', 'arm_code')