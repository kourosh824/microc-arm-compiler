.syntax unified
.thumb
.global asm_compute
.type asm_compute, %function


asm_compute:
    movs    r0, #0      
    movs    r1, #3      
    movs    r2, #1     
    movs    r3, #8     

    cmp     r0, r3
    beq     label_0
    b       label_1

label_0:
    movs    r3, #15
    b       label_2

label_1:
    movs    r3, #62
    b       label_2

label_2:
    adds    r0, r0, r2  
    adds    r3, r0, r2  
    mul     r3, r0, r2  

    mov     r0, r3     
    bx      lr
