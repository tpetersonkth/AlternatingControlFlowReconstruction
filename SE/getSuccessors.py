"""
Author: Thomas Peterson
Year: 2019
"""

import argparse, itertools, sys, time
import logging

from manticore.native import Manticore
from manticore.core.plugin import Plugin, ExtendedTracer
from manticore import issymbolic

#TODO: Use logger
#TODO: Purely symbolic execution?
#TODO: Multiple target addresses

logger = logging.getLogger(__name__)

def main():
    if (len(sys.argv) < 3):
        print("Usage: Python3 getSuccessors.py [path to binary] [address of instruction]")
        sys.exit(0)
    program = sys.argv[1]
    address = int(sys.argv[2],16)
    print("Running with program="+program+" address="+hex(address))
    paths = [[0x08048080,0x08048085,0x0804808a,0x0804808f,0x08048094,0x08048096,0x0804809b],
             [0x08048080,0x08048085,0x0804808a,0x0804808f,0x08048094]]
    pathslen = len(paths);
    run(program,address,paths,pathslen)

def run(program, address, paths, pathslen):
    #m = Manticore(program, pure_symbolic=True)
    m = Manticore(program, pure_symbolic=False)

    #Store variables in global context to enfsure that we can communicate them to the callback function
    with m.locked_context() as context:
        context['instructionAddress'] = address
        context['targets'] = set()

    #Register hook to have each executed instruction's RIP printed to the commandline
    m.add_hook(None, print_ip)
    m.register_plugin(ACFRPlugin())

    #Direct execution
    @m.hook(None)
    def hook(state):
        #TODO: Move to plugin
        #Update PCCounter
        if 'PCCounter' not in state.context:
            state.context['PCCounter'] = 0
            state.context['pathIDs'] = range(pathslen)
        else:
            state.context['PCCounter'] += 1

        #Check if RIP of the state is matching a path, else abandon it
        newPathIDS = []
        PCCounter = state.context['PCCounter']
        for pathID in state.context['pathIDs']:
            if PCCounter >= len(paths[pathID]):#TODO: Precompute this!!!
                continue
            if paths[pathID][PCCounter] == state.cpu.RIP:
                print("keeping: "+str(pathID))
                newPathIDS.append(pathID)

        state.context['pathIDs'] = newPathIDS

        if (not state.context['pathIDs']):#No path includes the state state
            print("Abandoning state with RIP=" + hex(state.cpu.RIP))
            state.abandon()

    m.run()
    with m.locked_context() as context:
        targets = context['targets']

    print("Run finished")
    print("Determined that the instruction at " + hex(address) + " can jump to the following addresses: " + ",".join(targets))

#A plugin to extract the successor instructions of a given instruction
class ACFRPlugin(Plugin):
    def will_execute_instruction_callback(self, state, pc, instruction):
        #Directed execution
        pass

    def did_execute_instruction_callback(self, state, old_pc, new_pc, instruction):

        #Get the address we are looking for
        with self.manticore.locked_context() as context:
            address = context['instructionAddress']

        #Check if we just executed the address we are looking for
        if (old_pc == address):
            print("Calculating possible targets")
            out=hex(old_pc)+ "->"

            with self.manticore.locked_context() as context:
                targets = context['targets']

            #Calculate possible succeessor of the instruction at the target address
            for i in state.solve_n(new_pc, nsolves=5):
                targets.add(hex(i))

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
