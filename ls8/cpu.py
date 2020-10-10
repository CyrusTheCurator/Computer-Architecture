"""CPU functionality."""

import sys

"""
Instruction Set: an instruction is a command which tesll the CPU to do some fundamental task, such as add 2 numbers. Instructions have both an opcode which indicates the kind of task to perform and a set of parameters which provide inputs to the task being performed
Each opcode represents one task that the CPU "knows" how to do. There are just 16 opcodes in LS-8. Everything the computer can calculate is some sequence of these simple instructions. Each instruction is 16 bits long, with the left 4 bits storing the opcode. The rest of the bits are used to store the parameters
"""

cmds = {
"ADD":  0b10100000, 
"AND":  0b10101000,
"CALL":  0b01010000,
"CMP":  0b10100111, 
"DEC":  0b01100110,
"DIV":  0b10100011,
"HLT":  0b00000001,
"INC":  0b01100101,
"JEQ":  0b01010101,
"JMP":  0b01010100,
"JNE":  0b01010110,
"LDI":  0b10000010,
"MUL":  0b10100010,
"POP":  0b01000110,
"PRN":  0b01000111, 
"PUSH":  0b01000101, 
"RET":  0b00010001}


#haha you THOUGHT
# reverse_cmds = {}
# for key in cmds:
#     reverse_cmds[cmds[key]]=key



# R7 is reserved as the Stack Pointer (SP). SP points at the value at the top of the stack (most recently pushed), or address F4 if the stack is empty
sp = 7

# Centeral Processing Unit
class CPU:
    """Main CPU class."""

    def __init__(self):
        """Step 1: Construct a new CPU."""
        # initialize the ram with 256 bytes
        self.ram = [0] * 256  
        self.reg = [0] * 8 
        self.pc = 0
        self.SP = 7
        self.FL = 0b00000000
        self.reg[self.SP] = 0xF4
        

    

    def ram_read(self, MAR):
        return self.ram[MAR]
    

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR
        return self.ram_read(MAR)
        


    def load(self):
        """Load a program into memory."""
        
        address = 0

        # For now, we've just hardcoded a program:
        program = []
        if len(sys.argv) != 2:
            print('Please include the file you would like to run in your initialization command')
            sys.exit(1)

        try:
            with open("examples/"+sys.argv[1]) as f:
                
                for line in f:
                    if line[0] == "#":
                        continue
                    comment_split = line.split("#") # 10000010 # LDI R0,8 --> ['10000010 ', ' LDI R0,8']
                    num = comment_split[0]
                    
                    try:
                        x = int(num, 2)
                        self.ram[address] = x
                        # print("{:08b}: {:d}".format(x, x))
                        address += 1
                    except:
                        # print('cant convert string to number')
                        continue
                self.reg[self.SP] = len(self.ram) - 1
        except:
            print('file not found')
            sys.exit(1)

        for instruction in program:
            self.ram[address] = instruction
            address += 1
            

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == cmds["ADD"]:
            self.reg[reg_a] += self.reg[reg_b]
        elif op == cmds["MUL"]:
             self.reg[reg_a] *= self.reg[reg_b]
        elif op == cmds["CMP"]:
            if self.reg[reg_a] == self.reg[reg_b]:
                self.FL = 0b00000001
                # 00000LGE
                #do a E
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.FL = 0b00000010

                #do a G
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.FL = 0b00000100

                #do a L
            else:
                self.FL = 0b00000000

        else:
            raise Exception("Unsupported ALU operation")
        

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.FL,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')





    def run(self):
        """Run the CPU."""
        self.running = True
        while self.running:
            IR = self.ram_read(self.pc)
                
                
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            if IR == cmds["LDI"]:
                # print("throwing ", operand_b, " into register ", operand_a)
                self.reg[operand_a] = operand_b
                # print(self.reg[2])
                self.pc += 3

            elif IR == cmds["PRN"]:
                val = self.reg[operand_a]
                print(f'PRN --> {val}')
                self.pc += 2

            elif IR == cmds["HLT"]:
                self.running = False

            elif IR == cmds["MUL"]:
                self.alu(IR, operand_a, operand_b)
                self.pc += 3
            elif IR == cmds["ADD"]:
                regA = self.ram[self.pc + 1]
                regB = self.ram[self.pc + 2]
                sumOfRegisters = self.reg[regA] + self.reg[regB]
                self.reg[regA] = sumOfRegisters
                self.pc += 2
            elif IR == cmds["PUSH"]:
                self.reg[self.SP] -= 1
                value_in_reg = self.reg[operand_a]
                self.ram[self.reg[self.SP]] = value_in_reg
                self.pc += 2
            elif IR == cmds["POP"]:
                top_most_val = self.ram[self.reg[self.SP]]
                reg_to_store_in = self.ram[self.pc+1]
                self.reg[reg_to_store_in] = top_most_val
                self.reg[self.SP] += 1
                self.pc += 2
            elif IR == cmds["CALL"]:

                self.reg[self.SP] -= 1
                addressOfNextInstruction = self.pc + 2
                self.ram[self.reg[self.SP]] = addressOfNextInstruction

                registerToGetAddressFrom = self.ram[self.pc + 1]
                addressToJumpTo = self.reg[registerToGetAddressFrom]
                self.pc = addressToJumpTo
            elif IR == cmds["RET"]:
                # pop the topmost value in the stack
                addressToReturnTo = self.ram[self.reg[self.SP]]
                self.ram[self.reg[self.SP]] += 1
                # set the pc to that value
                self.pc = addressToReturnTo
            elif IR == cmds["CMP"]:
                # print("comparing ", operand_a, " and ", operand_b)
                self.alu(IR, operand_a, operand_b)
                self.pc += 3
                # sys.exit()
            elif IR == cmds["JMP"]:
                # do iiiit
                self.pc = self.reg[operand_a]
            elif IR == cmds["JNE"]:
                # do iiiit
                if self.FL &~ 0b00000001:
                    self.pc = self.reg[operand_a]
                else:
                    self.pc += 2
            elif IR == cmds["JEQ"]:
                # do iiiit
                if self.FL & 0b00000001:
                    self.pc = self.reg[operand_a]
                else:
                    self.pc += 2

            elif IR == 0:
                self.pc+=1
                continue
            
            else:
                print("uh?")
                print("done")
                sys.exit(1)
            

# ### CMP

# *This is an instruction handled by the ALU.*

# `CMP registerA registerB`

# Compare the values in two registers.

# * If they are equal, set the Equal `E` flag to 1, otherwise set it to 0.

# * If registerA is less than registerB, set the Less-than `L` flag to 1,
#   otherwise set it to 0.

# * If registerA is greater than registerB, set the Greater-than `G` flag
#   to 1, otherwise set it to 0.

# Machine code:
# ```
# 10100111 00000aaa 00000bbb
# A7 0a 0b
# ```