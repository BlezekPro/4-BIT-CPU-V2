import time

# Funkcja do konwersji 4-bit unsigned na signed aby działało odejmowanie
def signed4bit(val):
    return val - 16 if val > 7 else val

class CPU:
    def __init__(self, clock_hz=1):
        self.A = 0
        self.PC = 0
        self.C = 0
        self.Z = 0
        self.RAM = [0] * 16
        self.program = []
        self.halted = False
        self.clock_hz = clock_hz
        self.clock_delay = 1 / clock_hz if clock_hz > 0 else 0
        # do przechowania finalnego wyniku
        self.final_A = 0
        self.final_C = 0

    def fetch(self):
        instr = self.program[self.PC]
        self.PC = (self.PC + 1) & 0xF
        return instr

    def step(self):
        instr = self.fetch()
        opcode = instr >> 4
        operand = instr & 0xF

        if opcode == 0x0:  # NOP
            pass
        elif opcode == 0x1:  # LOAD
            self.A = operand
        elif opcode == 0x2:  # ADD
            r = self.A + operand
            self.C = 1 if r > 15 else 0
            self.A = r & 0xF
        elif opcode == 0x3:  # SUB
            r = self.A - operand
            self.C = 1 if r < 0 else 0
            self.A = r & 0xF
        elif opcode == 0x4:  # AND
            self.A &= operand
        elif opcode == 0x5:  # OR
            self.A |= operand
        elif opcode == 0x6:  # JMP
            self.PC = operand
        elif opcode == 0x7:  # JZ
            if self.Z == 1:
                self.PC = operand
        elif opcode == 0x8:  # JNZ
            if self.Z == 0:
                self.PC = operand
        elif opcode == 0x9:  # STORE
            self.RAM[operand] = self.A
        elif opcode == 0xA:  # LOADM
            self.A = self.RAM[operand]
        elif opcode == 0xB:  # ADDM
            r = self.A + self.RAM[operand]
            self.C = 1 if r > 15 else 0
            self.A = r & 0xF
        elif opcode == 0xC:  # SUBM
            r = self.A - self.RAM[operand]
            self.C = 1 if r < 0 else 0
            self.A = r & 0xF
        elif opcode == 0xD:  # HALT
            self.halted = True
            # zapamiętujemy wynik
            self.final_A = self.A
            self.final_C = self.C
        elif opcode == 0xE:  # IN
            self.A = int(input("IN (0-15): ")) & 0xF
        elif opcode == 0xF:  # OUT
            print("OUT:", signed4bit(self.A))  # wyświetlamy signed

        # aktualizacja flagi zero
        self.Z = 1 if self.A == 0 else 0

    def run(self, max_steps=1000):
        steps = 0
        while not self.halted and steps < max_steps:
            self.debug()
            self.step()
            steps += 1
            if self.clock_delay > 0:
                time.sleep(self.clock_delay)
        print("CPU HALTED")

    def debug(self):
        print(f"PC={self.PC} A={self.A} C={self.C} Z={self.Z} RAM={self.RAM}")


# ASSEMBLER
OPS = {
    "NOP": 0x0,
    "LOAD": 0x1,
    "ADD": 0x2,
    "SUB": 0x3,
    "AND": 0x4,
    "OR": 0x5,
    "JMP": 0x6,
    "JZ": 0x7,
    "JNZ": 0x8,
    "STORE": 0x9,
    "LOADM": 0xA,
    "ADDM": 0xB,
    "SUBM": 0xC,
    "HALT": 0xD,
    "IN": 0xE,
    "OUT": 0xF
}

def assemble(lines):
    program = []
    for line in lines:
        parts = line.split()
        op = OPS[parts[0]]
        val = int(parts[1]) if len(parts) > 1 else 0
        program.append((op << 4) | val)
    return program


# PROGRAM: KALKULATOR Z WYBOREM DODAWANIA / ODEJMOWANIA
code = [
    "IN",        # pierwsza liczba
    "STORE 0",   # RAM[0] = x
    "IN",        # druga liczba
    "STORE 1",   # RAM[1] = y
    "IN",        # wybór: 0 = ADD, 1 = SUB
    "JZ 10",     # jeśli 0 to skocz do ADD (linia 10)
    # Odejmowanie (wybór = 1)
    "LOADM 1",   # A = y
    "SUBM 0",    # A = y - x
    "OUT",
    "HALT",
    # Dodawanie (wybór = 0)
    "LOADM 1",   # linia 10: A = y
    "ADDM 0",    # A = y + x
    "OUT",
    "HALT"
]


# URUCHOMIENIE CPU
cpu = CPU(clock_hz=2)
cpu.program = assemble(code)
cpu.run()

print("FINAL RESULT:", signed4bit(cpu.final_A), "CARRY:", cpu.final_C)
