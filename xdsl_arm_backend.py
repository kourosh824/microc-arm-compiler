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
    ICmpOp,
    ReturnOp
)

class ARMBackend:
    def __init__(self, module):
        self.module = module
        # Counter to skip the first store operation
        self.store_instance = 0
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
        # Final parsed code
        self.compiled_code = [
            '.syntax unified',
            '.thumb',
            '.global asm_compute',
            '.type asm_compute, %function'
        ]

    # What is returned when this object is printed
    def __str__(self):
        return self.compiled_code

    # This function will assign a register to a memory address
    # It will also assign it a name based on the reg_index
    def alloc_reg(self):
        r = f'r{self.reg_index}'
        self.reg_index += 1
        return r
    
    # This function will assign a label to each block
    def alloc_label(self):
        l = f'label_{self.label_index}'
        if self.label_index == -1:
            l = 'asm_compute'
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
            # Map each constant to its value
            self.value_const_map[op.results[0]] = op.value.value.data
            return # Just go to next instruction

        if isinstance(op, AllocaOp):
            return

        # For store we just want to see which constant is stored at which memory space.
        if isinstance(op, StoreOp):
            # if the first operand is not a constant and is coming from a mathematical
            # expression then return since the math handler writes the compiled code itself
            if op.operands[0] not in self.value_const_map.keys():
                return
            
            # Skip the first store operation since it will never be used
            if self.store_instance == 0:
                self.store_instance += 1
                return
            
            # the constant is saved at op.operands[0]
            c = self.value_const_map[op.operands[0]]
            # the pointer is saved at op.operansd[1]
            # r = self.value_reg_map[op.operands[1]]
            k = op.operands[1]
            r = 0
            if k in self.value_reg_map.keys():
                r = self.value_reg_map[k]
            else:
                r = self.alloc_reg()
                self.value_reg_map[k] = r
            self.compiled_code.append(f'\tmovs {r}, #{c}')
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
            k = op.next_op.operands[1]
            rout = 0
            if k in self.value_reg_map.keys():
                rout = self.value_reg_map[k]
            else:
                rout = self.alloc_reg()
                self.value_reg_map[k] = rout
           
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
        
        if isinstance(op, ReturnOp):
            self.compiled_code.append(f'\tmov r0, {self.value_reg_map[op.operands[0]]}')
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
        # the following line is added for returning
        self.compiled_code.append('\tbx lr')

    # Save code in the currect directory
    def save_code(self, path, file_name):
        f = open(f'{path}/{file_name}.arm', 'w')
        for line in self.compiled_code:
            f.write(f'{line}\n')

