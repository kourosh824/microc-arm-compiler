from xdsl.dialects.builtin import (
    I1
)
from xdsl.irdl.operations import (
    IRDLOperation,
    AttrSizedOperandSegments,
    irdl_op_definition,
    successor_def,
    var_operand_def,
    operand_def
)

# llvm.br ^bb1
# llvm.cond_br %c, ^bb1, ^bb2
@irdl_op_definition
class BrOp(IRDLOperation):
    name = 'llvm.br'
    # Branch ops jump to BLOCKS and these block references are called successors
    # So dest contains a reference to a target basic block
    dest = successor_def()
    # A variable-length list of operands
    # llvm.br ^bb1(%x, %y, %z), %x, %y, %z are block arguments
    dest_args = var_operand_def()

    def __init__(self, dest, args=[]):
        super().__init__(successors=[dest], operands=[args])

# llvm.cond_br has three operand segments, [cond][true_args][false_args]
@irdl_op_definition
class CondBrOp(IRDLOperation):
    name = 'llvm.cond_br'

    # Branch condition
    cond = operand_def(I1)

    # Branch targets
    true_dest = successor_def()
    false_dest = successor_def()

    args = var_operand_def()

    def __init__(self, cond, tdest, fdest, args=None):
        if args is None:
            args = []
        super().__init__(
            operands=[cond, *args],
            successors=[tdest, fdest]
        )
