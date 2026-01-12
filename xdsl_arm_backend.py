from xdsl_llvm_operations import BrOp, CondBrOp
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

class ARMBackend:
    def __init__(self, module):
        self.module = module
        # Current register index, how many registers we have used till now
        self.reg_index = 0
        # Current label index, how many labels we have in total
        self.label_index = -1
        # Maps each constant to its value
        self.value_const_map = {}
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
        self.compiled_code = []

    # What is returned when this object is printed
    def __str__(self):
        return self.compiled_code

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
            
            # Map each constant to its value
            self.value_const_map[op.results[0]] = op.value.value.data
            return # Just go to next instruction

        if isinstance(op, AllocaOp):
            # If we have memory allocation then we must allocate a register
            reg = self.alloc_reg()
            # Map each POINTER to its register
            self.value_reg_map[op.results[0]] = reg
            return

        # For store we just want to see which constant is stored at which memory space.
        if isinstance(op, StoreOp):
            # if the first operand is not a constant and is coming from a mathematical
            # expression then return since the math handler writes the compiled code itself
            if op.operands[0] not in self.value_const_map.keys():
                return
            # the constant is saved at op.operands[0]
            c = self.value_const_map[op.operands[0]]
            # the pointer is saved at op.operansd[1]
            r = self.value_reg_map[op.operands[1]]
            self.compiled_code.append(f'\tli {r}, {c}')
            # self.store_operands.append(op)
            return

        # We will just link the new pointer to allocated register from AllocOp
        if isinstance(op, LoadOp):
            # Map the result of the load operation to the same allocated register
            self.value_reg_map[op.results[0]] = self.value_reg_map[op.operands[0]]
            return

        if isinstance(op, AddOp) or isinstance(op, SubOp) or isinstance(op, MulOp):
            r1 = self.value_reg_map[op.lhs]
            r2 = self.value_reg_map[op.rhs]
            # after a math operation the next instruction is store
            # we read the store to find out where the result is being saved
            rout = self.value_reg_map[op.next_op.operands[1]]
            self.compiled_code.append(f'\t{self.instruction_type(op)} {rout}, {r1}, {r2}')

            return

        if isinstance(op, BrOp):
            l = self.value_label_map[op.dest]
            self.compiled_code.append(f"\tb {l}")  
            return

        if isinstance(op,ICmpOp):
            r1 = self.value_reg_map[op.lhs]
            r2 = self.value_reg_map[op.rhs]
            self.compiled_code.append(f'\tcmp {r1}, {r2}')
            return

        if isinstance(op, CondBrOp):
            true_label = self.value_label_map[op.true_dest]
            false_label = self.value_label_map[op.false_dest]
            self.compiled_code.append(f'\tbeq {true_label}')
            self.compiled_code.append(f'\tb {false_label}')
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
                    self.compiled_code.append(f'{block_label}:')
                    
                    for op in block.ops:
                        self.compile(op)


    # Save code in the currect directory
    def save_code(self, path, file_name):
        f = open(f'{path}/{file_name}.arm', 'w')
        for line in self.compiled_code:
            f.write(f'{line}\n')

