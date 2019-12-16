"""
Author: Thomas Peterson
Year: 2019
Description: A file containing custom plugins for Manticore
"""

import logging
from manticore.core.plugin import Plugin
from globalLogger import logger

#A plugin to extract the successor instructions of a given instruction
class ExtractorPlugin(Plugin):

    def did_execute_instruction_callback(self, state, old_pc, new_pc, instruction):
        #Extract jump targets

        #Get the address we are looking for
        with self.manticore.locked_context() as context:
            address = context['instructionAddress']

        #Check if we just executed the address we are looking for
        if (old_pc == address):
            logger.info("Calculating possible targets")
            out=hex(old_pc)+ "->"

            with self.manticore.locked_context() as context:
                targets = context['targets']

            #Calculate possible succeessor of the instruction at the target address
            for i in state.solve_n(new_pc, nsolves=5):
                targets.add(hex(i))

            #Put them in the global context so that they can be accessed later
            with self.manticore.locked_context() as context:
                context['targets'] = targets

            #Log our results!
            out += ",".join(targets)
            logger.debug(out)

#A plugin to extract the successor instructions of a given instruction and to direct execution along a set of predefined paths
class DirectedExtractorPlugin(Plugin):

    #Directed execution
    def will_execute_instruction_callback(self, state, pc, instruction):
        with self.manticore.locked_context() as context:
            pathsObject = context['paths']

        # Update PCCounter
        if 'PCCounter' not in state.context:
            state.context['PCCounter'] = 0
            state.context['pathIDs'] = range(
                pathsObject.pathsLen)  # All paths start with the first instruction of the binary
        else:
            state.context['PCCounter'] += 1

        # Check if RIP of the state is matching a path, else abandon it
        newPathIDS = []
        PCCounter = state.context['PCCounter']
        keeping = []
        for pathID in state.context['pathIDs']:
            if PCCounter >= pathsObject.paths[pathID].pathLen:
                continue

            if pathsObject.paths[pathID].path[PCCounter] == state.cpu.RIP:
                newPathIDS.append(pathID)
                keeping.append(str(pathID))

        state.context['pathIDs'] = newPathIDS

        logger.debug("keeping: " + ",".join(keeping))

        if (not state.context['pathIDs']):  # No path includes the state state
            logger.debug("Abandoning state with RIP=" + hex(state.cpu.RIP) + " PCCounter=" + str(PCCounter))
            state.abandon()


    #Extract jump targets
    def did_execute_instruction_callback(self, state, old_pc, new_pc, instruction):

        #Get the address we are looking for
        with self.manticore.locked_context() as context:
            pathsObject = context['paths']

        #Check if we just executed the address we are looking for
        pathsEndingHere = []#Contains at most one element except if we have been requested to evaluate the same path twice
        for i in range(0,pathsObject.pathsLen):
            if (pathsObject.paths[i].pathLen-1 == state.context['PCCounter'] and old_pc == pathsObject.lastAddresses[i]):
                pathsEndingHere.append(i)

        with self.manticore.locked_context() as context:
            targets = context['targets']

        for i in pathsEndingHere:
            out = "Possible targets ["+str(i)+"]"+"]: "
            out = hex(old_pc)+ "->"

            #Calculate possible successors of the instruction at the target address
            for concreteNewPC in state.solve_n(new_pc, nsolves=5):#TODO: Other value for nsolves? Check if conditional branch. 1 if unconditional. Maybe add constraint that next value can not equal first?
                for pathId in pathsEndingHere:
                    if pathId not in targets.keys():
                        targets[pathId] = set()
                    targets[pathId].add(hex(concreteNewPC))

            #Log our results!
            out += ",".join([str(i) for i in targets[i]])
            logger.debug(out)

        # Put the results in the global context so that they can be accessed later
        with self.manticore.locked_context() as context:
            context['targets'] = targets
