import sys
from manticore.native import Manticore
from manticore.core.plugin import Plugin

def main():
    program = sys.argv[1]
    address = int(sys.argv[2],16)
    print("Running with program="+program+" address="+hex(address))
    run(program,address)

def run(program, address):
    #m = Manticore(program, pure_symbolic=True)
    m = Manticore(program, pure_symbolic=False)

    #Store variables in global context to ensure that we can communicate them to the callback function
    with m.locked_context() as context:
        context['instructionAddress'] = address
        context['targets'] = []

    #Register hook to have each executed instruction's RIP printed to the commandline
    m.add_hook(None, print_ip)
    m.register_plugin(ACFRPlugin())

    #Notify the user when reaching the target address
    @m.hook(address)
    def hook(state):
        print("Reached target address")

    #Naive guided execution...
    @m.hook(None)
    def hook(state):
        if state.cpu.RIP not in [0x08048080,0x08048085,0x0804808a,0x0804808f,0x08048094,0x08048096,0x0804809b]:
            print("Abandoning state with RIP="+hex(state.cpu.RIP))
            state.abandon()
    m.run()
    with m.locked_context() as context:
        targets = context['targets']
    print("Run finished")
    print("Determined that the instruction at " + hex(address) + " can jump to the following addresses: " + ",".join(targets))

#A plugin to extract the successor instructions of a given instruction
class ACFRPlugin(Plugin):
    def did_execute_instruction_callback(self, state, old_pc, new_pc, instruction):

        #Get the address we are looking for
        with self.manticore.locked_context() as context:
            address = context['instructionAddress']

        #Check if we just executed the address we are looking for
        if (old_pc == address):
            print("Calculating possible targets")
            out=hex(old_pc)+ "->"
            targets = []

            #Calculate possible succeessor of the instruction at the target address
            for i in state.solve_n(new_pc, nsolves=5):
                targets.append(hex(i))

            #Put them in the global context so that they can be accessed later
            with self.manticore.locked_context() as context:
                context['targets'] = targets

            #Print our results!
            out += ",".join(targets)
            print(out)

#Prints the RIP of a state
def print_ip(state):
    print(hex(state.cpu.RIP))

if __name__ == "__main__":
    main()
