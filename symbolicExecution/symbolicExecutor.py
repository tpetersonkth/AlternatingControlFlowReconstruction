"""
Author: Thomas Peterson
Year: 2019
"""

import manticore.utils.config as config
from manticore.native import Manticore
from customPlugins import ExtractorPlugin, DirectedExtractorPlugin
from globalLogger import logger

#Performs a symbolic execution along a set of paths using Manticore
def executeDirected(program, pathsObject, args=[]):
    workplace_url = "/tmp/mcore_tmp"
    m = Manticore(program, argv=args, workspace_url=workplace_url, pure_symbolic=False)
    consts = config.get_group("core")
    consts.__setattr__("procs", 1)

    #Store variables in global context to ensure that we can communicate them to the callback function
    with m.locked_context() as context:
        context['paths'] = pathsObject
        context['targets'] = dict()

    #Register hook to have each executed instruction's RIP logged
    m.add_hook(None, log_rip)
    m.register_plugin(DirectedExtractorPlugin())

    #Output the set of paths
    for i in pathsObject.paths:
        l = [hex(j) for j in i.path]
        logger.debug(",".join(l))

    #Execute the directed symbolic execution
    m.run()

    #Obtain the dictionary of control flow edges from Manticore
    with m.locked_context() as context:
        targets = context['targets']

    #Output results
    logger.debug("--Results Sorted by Pathlen--")
    sortedPaths = sorted(pathsObject.paths, key=lambda x: x.pathLen, reverse=False)
    for i in range(pathsObject.pathsLen):
        pathID = sortedPaths[i].pathID
        if pathID in targets.keys():
            logger.debug("Path " + str(pathID) + "[len=" + str(sortedPaths[i].pathLen) + "] ending with " + hex(
                pathsObject.lastAddresses[pathID]) + " has the following successors " +
                  ",".join([str(i) for i in targets[pathID]]))
        else:
            logger.debug("Path " + str(pathID) + "[len=" + str(sortedPaths[i].pathLen) + "]" + " is infeasible")

    return targets

#Logs the RIP of a state
def log_rip(state):
    logger.debug(hex(state.cpu.RIP))
