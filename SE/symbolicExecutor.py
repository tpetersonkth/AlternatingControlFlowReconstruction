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

    m.run()
    with m.locked_context() as context:
        targets = context['targets']

    print("--Results Sorted by Pathlen--")
    sortedPaths = sorted(pathsObject.paths, key=lambda x: x.pathLen, reverse=False)
    for i in range(pathsObject.pathsLen):
        pathID = sortedPaths[i].pathID
        if pathID in targets.keys():
            print("Path " + str(pathID) + "[len=" + str(sortedPaths[i].pathLen) + "] ending with " + hex(
                pathsObject.lastAddresses[pathID]) + " has the following successors " +
                  ",".join([str(i) for i in targets[pathID]]))
        else:
            print("Path " + str(pathID) + "[len=" + str(sortedPaths[i].pathLen) + "]" + " is infeasible")

    return targets

#Prints the RIP of a state
def print_rip(state):
    print(hex(state.cpu.RIP))