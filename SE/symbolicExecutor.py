"""
Author: Thomas Peterson
Year: 2019
"""
import pathsObject, pathObject

from manticore.native import Manticore
from customPlugins import ExtractorPlugin, DirectedExtractorPlugin

#TODO: Use logger
#TODO: Purely symbolic execution?
#TODO: Avoid generating the output directory
#TODO(Possible): Timeout

def execute(program, address):
    #m = Manticore(program, pure_symbolic=True)
    m = Manticore(program, pure_symbolic=False)

    #Store variables in global context to ensure that we can communicate them to the callback function
    with m.locked_context() as context:
        context['instructionAddress'] = address
        context['targets'] = set()

    #Register hook to have each executed instruction's RIP printed to the command line
    #m.add_hook(None, print_rip)
    m.register_plugin(ExtractorPlugin())

    m.run()
    with m.locked_context() as context:
        targets = context['targets']

    print("Run finished")
    print("Determined that the instruction at " + hex(address) + " can jump to the following addresses: " + ",".join(targets))

def executeDirected(program, pathsObject):
    #m = Manticore(program, pure_symbolic=True)
    m = Manticore(program, pure_symbolic=False)

    #Store variables in global context to ensure that we can communicate them to the callback function
    with m.locked_context() as context:
        context['paths'] = pathsObject
        context['targets'] = dict()

    #Register hook to have each executed instruction's RIP printed to the command line
    m.add_hook(None, print_rip)
    m.register_plugin(DirectedExtractorPlugin())


    for i in pathsObject.paths:
        l = [hex(j) for j in i.path]
        print(",".join(l))

    #Direct the execution
    @m.hook(None)
    def hook(state):
        #TODO: Move to plugin
        with m.locked_context() as context:
            pathsObject = context['paths']

        #Update PCCounter
        if 'PCCounter' not in state.context:
            state.context['PCCounter'] = 0
            state.context['pathIDs'] = range(pathsObject.pathsLen) #All paths start with the first instruction of the binary
        else:
            state.context['PCCounter'] += 1

        #Check if RIP of the state is matching a path, else abandon it
        newPathIDS = []
        PCCounter = state.context['PCCounter']
        for pathID in state.context['pathIDs']:
            if PCCounter >= pathsObject.paths[pathID].pathLen:
                continue

            if pathsObject.paths[pathID].path[PCCounter] == state.cpu.RIP :
                print("keeping: "+str(pathID))
                newPathIDS.append(pathID)

        state.context['pathIDs'] = newPathIDS

        if (not state.context['pathIDs']):#No path includes the state state
            print("Abandoning state with RIP=" + hex(state.cpu.RIP) + " PCCounter=" + str(PCCounter))
            state.abandon()

    m.run()
    with m.locked_context() as context:
        targets = context['targets']

    print("Run finished")
    for t in pathsObject.lastAddresses:
        t = hex(t)
        if t in targets.keys():
            print("Determined that the instruction at " + t + " can jump to the following addresses: " + ",".join(targets[t]))
        else:
            print("Could not resolve the targets of the instruction at " + t)

    return targets

#Prints the RIP of a state
def print_rip(state):
    print(hex(state.cpu.RIP))