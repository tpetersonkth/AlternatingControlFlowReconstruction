"""
Author: Thomas Peterson
Year: 2019
"""

#TODO: Purely symbolic execution?
#TODO(Possible): Timeout

import manticore.utils.config as config
from manticore.native import Manticore
from customPlugins import ExtractorPlugin, DirectedExtractorPlugin

import logging

logger = logging.getLogger(__name__)
logger.setLevel('INFO')


# Obsolete
def execute(program, address):
    #m = Manticore(program, pure_symbolic=True)
    m = Manticore(program, pure_symbolic=False)

    #Store variables in global context to ensure that we can communicate them to the callback function
    with m.locked_context() as context:
        context['instructionAddress'] = address
        context['targets'] = set()

    #Register hook to have each executed instruction's RIP logged
    #m.add_hook(None, log_rip)
    m.register_plugin(ExtractorPlugin())

    m.run()
    with m.locked_context() as context:
        targets = context['targets']

    logger.info("Run finished")
    logger.info("Determined that the instruction at " + hex(address) + " can jump to the following addresses: " + ",".join(targets))

def executeDirected(program, pathsObject,args=""):
    #m = Manticore(program, pure_symbolic=True)
    workplace_url = "/tmp/mcore_tmp"
    m = Manticore(program, argv=args.split(" "), workspace_url=workplace_url, pure_symbolic=False)
    consts = config.get_group("core")
    consts.__setattr__("procs", 1)

    #Store variables in global context to ensure that we can communicate them to the callback function
    with m.locked_context() as context:
        context['paths'] = pathsObject
        context['targets'] = dict()

    #Register hook to have each executed instruction's RIP logged
    m.add_hook(None, log_rip)
    m.register_plugin(DirectedExtractorPlugin())


    for i in pathsObject.paths:
        l = [hex(j) for j in i.path]
        logger.debug(",".join(l))

    m.run()
    with m.locked_context() as context:
        targets = context['targets']

    logger.info("--Results Sorted by Pathlen--")
    sortedPaths = sorted(pathsObject.paths, key=lambda x: x.pathLen, reverse=False)
    for i in range(pathsObject.pathsLen):
        pathID = sortedPaths[i].pathID
        if pathID in targets.keys():
            logger.info("Path " + str(pathID) + "[len=" + str(sortedPaths[i].pathLen) + "] ending with " + hex(
                pathsObject.lastAddresses[pathID]) + " has the following successors " +
                  ",".join([str(i) for i in targets[pathID]]))
        else:
            logger.debug("Path " + str(pathID) + "[len=" + str(sortedPaths[i].pathLen) + "]" + " is infeasible")

    return targets

#Logs the RIP of a state
def log_rip(state):
    logger.debug(hex(state.cpu.RIP))
