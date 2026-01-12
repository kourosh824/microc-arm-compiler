from xdsl.ir import Block
from xdsl.dialects.builtin import (
    I1,
    ArrayAttr,
    IntegerAttr,
    i32
)
from xdsl.dialects.llvm import (
    FuncOp,
    StoreOp,
    ConstantOp,
    AddOp,
    LoadOp,
    SubOp,
    MulOp,
    AllocaOp,
    ReturnOp,
    ICmpOp
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

class ARMBackend:
    def __init__(self, module):
        self.module = module
        # Current register index, how many registers we have used till now
        self.reg_index = 0
        # Current label index, how many labels we have in total
        self.label_index = -1
        # Mapping LLVM memory to register
        self.value_reg_map = {}
        # Mapping LLVM blocks to labels
        self.value_label_map = {}
        # Storing all store operands
        # Basically we don't want to use the stack. In MLIR LLVM, each value is 
        # first saved as a constant, then a memory space is allocated for it,
        # then this constant is stored at that memory space and THEN we load this address.
        # We don't want to do all of this that's why we just define
        # an li instruction per each constant.
        self.store_operands = []
        # Final parsed code
        self.parsed_code = []

    # What is returned when this object is printed
    def __str__(self):
        return self.parsed_code

    # This function will assign a register to a memory address
    # It will also assign it a name based on the reg_index
    def alloc_reg(self):
        r = f't{self.reg_index}'
        self.reg_index += 1
        return r
    
    # This function will assign a label to each block
    def alloc_label(self):
        l = f'label_{self.label_index}'
        if self.label_index == -1:
            l = 'main'
        self.label_index += 1
        return l

    # This function will return the name of the instruction
    def instruction_type(self, op):
        if isinstance(op, AddOp):
            return 'add'
        if isinstance(op, SubOp):
            return 'sub'
        if isinstance(op, MulOp):
            return 'mul'

    # This function emits unwanted register allocations
    def skip_register(self, const_op):
        result = const_op.results[0]
        
        # Check all uses of this specific constant
        for use in result.uses:
            user = use.operation

            # If it's used in any math or the final return, we must keep it
            if isinstance(user, (AddOp, SubOp, MulOp, ReturnOp)):
                return True

            # If it's used in a Store, it represents a variable (like a=1)
            # We keep it unless it's specifically the very first store, which is used for setup
            if isinstance(user, StoreOp):
                # Only skip the '0' store if it's the first thing we see
                if const_op.value.value.data == 0 and self.reg_index == 0:
                    return False
                return True

            # If it's only used for alloca size, it's safe to skip
            if isinstance(user, AllocaOp): 
               return False
            
            return True

    # Get all blocks once and map them to labels
    def get_labels(self):
        for op in self.module.walk():
            if isinstance(op, FuncOp):
                for block in op.body.blocks:
                    block_label = self.alloc_label()
                    # Add block so we can map it later in branch instructions
                    self.value_label_map[block] = block_label

    def compile(self, op):
        if isinstance(op, ConstantOp):
            # Check if operation is alloca or the first store
            if not self.skip_register(op):
                return

            reg = self.alloc_reg()
            # Map each constant to a register
            self.value_reg_map[op.results[0]] = reg
            self.parsed_code.append(f'\tli {reg}, {op.value.value.data}')
            return # Just go to next instruction

        # For store we just want to see which constant is stored at which memory space.
        if isinstance(op, StoreOp):
            self.store_operands.append(op)
            return

        # Contains new memory space address and their registers
        new_map = {}
        # After we load the saved constant again into a new memory space, we want to find
        # the original constant reg.
        if isinstance(op, LoadOp):
            for sop in self.store_operands:
                if op.operands[0] == sop.operands[1]:
                    for k, v in self.value_reg_map.items():
                        if sop.operands[0] == k:
                            new_map[op.results[0]] = v
            self.value_reg_map.update(new_map)
            return

        if isinstance(op, AddOp) or isinstance(op, SubOp) or isinstance(op, MulOp):
            r1 = self.value_reg_map[op.lhs]
            r2 = self.value_reg_map[op.rhs]
            rout = self.alloc_reg()
            self.value_reg_map[op.results[0]] = rout
            self.parsed_code.append(f'\t{self.instruction_type(op)} {rout}, {r1}, {r2}')
            return

        if isinstance(op, BrOp):
            l = self.value_label_map[op.dest]
            self.parsed_code.append(f"\tb {l}")  
            return


        if isinstance(op,ICmpOp):
            r1 = self.value_reg_map[op.lhs]
            r2 = self.value_reg_map[op.rhs]
            self.parsed_code.append(f'\tcmp {r1}, {r2}')
            return

        if isinstance(op, CondBrOp):
            true_label = self.value_label_map[op.true_dest]
            false_label = self.value_label_map[op.false_dest]
            self.parsed_code.append(f'\tbeq {true_label}')
            self.parsed_code.append(f'\tb {false_label}')
            return

    # This function walks the MLIR LLVM code and parses it to ARM assembly
    def walk(self):
        # First get all labels
        self.get_labels()
        for op0 in self.module.walk():
            if isinstance(op0, FuncOp):
                for block in op0.body.blocks:
                    block_label = self.value_label_map[block]
                    # Add block so we can map it later in branch instructions
                    self.parsed_code.append(f'{block_label}:')
                    
                    for op in block.ops:
                        self.compile(op)


    # Save code in the currect directory
    def save_code(self, path, file_name):
        f = open(f'{path}/{file_name}.arm', 'w')
        for line in self.parsed_code:
            f.write(f'{line}\n')

