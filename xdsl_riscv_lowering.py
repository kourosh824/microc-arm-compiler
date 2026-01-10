from xdsl.context import Context
from xdsl.passes import ModulePass
from xdsl.dialects.builtin import IntegerAttr
from xdsl.dialects.llvm import AddOp as LLVMAddOp # LLVM AddOp
from xdsl.dialects.llvm import ConstantOp as LLVMConstantOp # LLVM ConstantOp
from xdsl.dialects.llvm import StoreOp as LLVMStoreOp # LLVM StoreOp
from xdsl.dialects.riscv import AddOp as RISCVAddOp # RISCV MLIR AddOp
from xdsl.dialects.riscv import AddiOp as RISCVAddiOp # RISCV MLIR AddiOp
from xdsl.pattern_rewriter import RewritePattern, PatternRewriter, op_type_rewrite_pattern

# This class ONLY rewrites LLVM AddOp and replaces it with RISCV AddOp
class LowerLLVMAddToRISCV(RewritePattern):
    @op_type_rewrite_pattern
    def match_and_rewrite(self, op:LLVMAddOp, rewriter: PatternRewriter):
        riscv_add = RISCVAddOp(op.lhs, op.rhs)
        rewriter.replace_op(op, riscv_add)

class LowerLLVMConstantToRISCV(RewritePattern):
    @op_type_rewrite_pattern
    def match_and_rewrite(self, op:LLVMConstantOp, rewriter: PatternRewriter):
        val_attr = op.value
        if not isinstance(val_attr, IntegerAttr):
            return
        # Only handle small integers
        val = val_attr.value.data

        # In xDSL RISC-V dialect, AddiOp expects:
        # AddiOp(lhs: SSAValue, imm: int, result_types=[...])
        # So we can use lhs = first argument (or None) for 0
        # addi = RISCVAddiOp(rs1=0, immediate=val, rd=op.)

        rewriter.replace_op(op, addi)

# class LowerLLVMStoreToRISCV(RewritePattern):
#     @op_type_rewrite_pattern
#     def match_and_rewrite(self, op:LLVMStoreOp, rewriter: PatternRewriter):
        