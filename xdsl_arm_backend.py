from xdsl.dialects.llvm import StoreOp, ConstantOp, AddOp, LoadOp, SubOp, MulOp, AllocaOp, ReturnOp, ICmpOp

class ARMBackend:
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
    # It will also assign it a name based on the reg_index
    def alloc_reg(self):
        r = f't{self.reg_index}'
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
        return False

    # This function walks the MLIR LLVM code and parses it to ARM assembly
    def walk(self):
        for op in self.module.walk():
            if isinstance(op, ConstantOp):
                # Check if operation is the first store or alloca
                if not self.skip_register(op):
                    continue

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
                
            if op.name == "llvm.br":
                label = op.successors[0].name
                self.parsed_code.append(f"b {label}")
                continue

            if op.name == "llvm.cond_br":
                cond = self.value_reg_map[op.operands[0]]
                t = op.successors[0].name
                f = op.successors[1].name
                self.parsed_code.append(f"cmp {cond}, #0")
                self.parsed_code.append(f"bne {t}")
                self.parsed_code.append(f"b {f}")
                continue

    # Save code in the currect directory
    def save_code(self, path, file_name):
        f = open(f'{path}/{file_name}.arm', 'w')
        for line in self.parsed_code:
            f.write(f'{line}\n')

