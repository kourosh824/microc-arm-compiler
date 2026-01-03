from xdsl.context import Context
from xdsl.passes import ModulePass
from xdsl.dialects.llvm import AddOp as LLVMAddOp # LLVM AddOp
from xdsl.dialects.riscv import AddOp as RISCVAddOp # RISCV MLIR AddOp
from xdsl.pattern_rewriter import RewritePattern, PatternRewriter, op_type_rewrite_pattern

# This class ONLY rewrites LLVM AddOp and replaces it with RISCV AddOp
class LowerLLVMToRISCV(RewritePattern):
    @op_type_rewrite_pattern
    def match_and_rewrite(self, op:LLVMAddOp, rewriter: PatternRewriter):
        riscv_add = RISCVAddOp(op.lhs, op.rhs)
        rewriter.replace_op(op, riscv_add)