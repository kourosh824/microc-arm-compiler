from xdsl.dialects.llvm import StoreOp, ConstantOp, AddOp, LoadOp, SubOp, MulOp

class ARMParser:
    # List of available ARM registers
    reg_names = ['t0', 't1', 't2', 't3', 't4', 't5', 't6', 't7', 't8', 't9', 't10']
    # Current register index, how many registers we have used till now
    reg_index = 0
    # Mapping LLVM memory to register
    value_reg_map = {}
    # Storing all store operands
    # Basically we don't want to use the stack. In MLIR LLVM, each value is 
    # first saved as a constant, then a memory space is allocated for it,
    # then this constant is stored at that memory space and THEN we load this address.
    # We don't want to do all of this that's why we just define
    # an li instruction per each constant.
    store_operands = []
    # Final parsed code
    parsed_code = []

    def __init__(self, module):
        self.module = module

    # What is returned when this object is printed
    def __str__(self):
        return self.parsed_code

    # This function will assign a register to a memory address
    def alloc_reg(self):
        r = self.reg_names[self.reg_index]
        self.reg_index += 1
        return r
    
    # This function will return the name of the instruction
    def instruction_type(self, op):
        if isinstance(op, AddOp):
            return 'add'
        if isinstance(op, SubOp):
            return 'sub'
        if isinstance(op, MulOp):
            return 'mul'
    
    # This function walks the MLIR LLVM code and parses it to ARM assembly
    def walk(self):
        for op in self.module.walk():
            if isinstance(op, ConstantOp):
                reg = self.alloc_reg()
                # Map each constant to a register
                self.value_reg_map[op.results[0]] = reg
                self.parsed_code.append(f'li {reg}, {op.value.value.data}')
                continue # Just go to next instruction
            
            # For store we just want to see which constant is stored at which memory space.
            if isinstance(op, StoreOp):
                self.store_operands.append(op)
                continue
            
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
                continue

            if isinstance(op, AddOp) or isinstance(op, SubOp) or isinstance(op, MulOp):
                r1 = self.value_reg_map[op.lhs]
                r2 = self.value_reg_map[op.rhs]
                rout = self.alloc_reg()
                self.value_reg_map[op.results[0]] = rout
                self.parsed_code.append(f'{self.instruction_type(op)} {rout}, {r1}, {r2}')
                continue

    # Save code in the currect directory
    def save_code(self, path, file_name):
        f = open(f'{path}/{file_name}.arm', 'w')
        for line in self.parsed_code:
            f.write(f'{line}\n')