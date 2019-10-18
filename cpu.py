"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self, filename):
        """Construct a new CPU."""
        self.filename = filename    # instruction data file
        self.pc = 0                 #counter
        self.SP = 0xF4              #stack pointer
        self.ram = [0] * 256        # memory where to store programs and data

        # Registers
        self.registers = [0] * 8
        self.FL = 0
        # self.reg = [0] * 2


    def load(self):
        """Load a program into memory."""

        address = 0

        try:

            with open(self.filename) as f:
                for line in f:
                    comment_split = line.split('#')
                    num = comment_split[0].strip()
                    try:
                        val = int(num, 2)
                        self.ram[address] = val
                        address += 1
                    except ValueError:
                        # print("warning: value cannot be translated as int")
                        continue


                    

        except FileNotFoundError:
            print(f"{sys.argv[0]}: {sys.argv[1]} not found")
            sys.exit(2)


        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
  
        if op == 160:     #ADD
            self.registers[reg_a] += self.registers[reg_b]

        elif op == 162:   #MULT
            self.registers[reg_a] *= self.registers[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """


        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.registers[i], end='')

        print()

    def run(self):
        """Run the CPU."""


        running = True


        while running:


            command = self.ram[self.pc]

            if command == 130:      #LOAD

                self.registers[self.ram[self.pc + 1]] = self.ram[self.pc + 2]
                offset = (command >> 6) + 1
                self.pc += offset

            elif command == 71:       #PRINT
                print(self.registers[self.ram[self.pc + 1]])
                offset = (command >> 6) + 1
                self.pc += offset

            elif command == 160:     #ADD
                self.alu(160, self.ram[self.pc + 1], self.ram[self.pc + 2])
                offset = (command >> 6) + 1
                self.pc += offset

            elif command == 162:    # MULTIPLY
                self.alu(162, self.ram[self.pc + 1], self.ram[self.pc + 2])

                offset = (command >> 6) + 1
                self.pc += offset

            elif command == 69:     #PUSH
                self.SP -= 1
                self.ram[self.SP] = self.registers[self.ram[self.pc + 1]]

                
                offset = (command >> 6) + 1
                self.pc += offset

            elif command == 70:      #POP
                self.registers[self.ram[self.pc + 1]] = self.ram[self.SP]
                self.SP += 1

                offset = (command >> 6) + 1
                self.pc += offset

            
            elif command == 80:      #CALL

                self.SP -= 1
                self.ram[self.SP] = self.pc + 2
                address = self.registers[self.ram[self.pc + 1]]
                self.pc = address


            elif command == 17:      #RET

                self.pc = self.ram[self.SP]
                self.SP += 1

            elif command == 167:     #CMP

                if self.registers[self.ram[self.pc + 1]] < self.registers[self.ram[self.pc+2]]:
                    self.FL = self.FL | 4   #bitwise OR to set 6th bit to 1 (Less than)

                elif self.registers[self.ram[self.pc + 1]] == self.registers[self.ram[self.pc+2]]:
                    self.FL = self.FL | 1   #bitwise OR to set 6th bit to 1 (equal)

                else:
                    self.FL = self.FL | 2   #bitwise OR to set 7th bit to 1 (Greater than)

                offset = (command >> 6) + 1
                self.pc += offset

            elif command == 84:       #JUMP
                self.pc = self.registers[self.ram[self.pc + 1]]

            elif command == 85:
                if self.FL & 1 == 1:        #bitwise AND to check last bit is on (Equal)
                    self.pc = self.registers[self.ram[self.pc + 1]]
                else:
                    offset = (command >> 6) + 1
                    self.pc += offset

            elif command == 86:             #bitwise AND to check last bit is off (notEqual)
                if self.FL & 1 == 0:
                    self.pc = self.registers[self.ram[self.pc + 1]]
                else:
                    offset = (command >> 6) + 1
                    self.pc += offset



            elif command == 1:
                running = False

            
            else:
                sys.exit(1)


    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MDR, MAR):
        self.ram[MAR] = MDR

