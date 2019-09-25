from manticore.core.plugin import Plugin

#A plugin to extract the successor instructions of a given instruction and to direct execution along a set of predefined paths
class DirectedExtractorPlugin(Plugin):

    #Directed execution
    def will_execute_instruction_callback(self, state, pc, instruction):
        #This callback ensures that manticore only follow the provided paths
        #Each state has a counter PCCounter which represents how many instructions has been executed before this state
        #and also has a list of paths that it could be part of.
        #This function increases PCCounter by 1 and updates the paths that the new state can be part of

        with self.manticore.locked_context() as context:
            paths = context['paths']

            # Update PCCounter
            if 'PCCounter' not in state.context:
                state.context['PCCounter'] = 0
                state.context['pathIDs'] = range(len(paths))  # All paths start with the first instruction of the binary
            else:
                state.context['PCCounter'] += 1

            # Check if RIP of the new state is matching a path, else abandon it
            newPathIDS = []
            PCCounter = state.context['PCCounter']
            keeping = []
            for pathID in state.context['pathIDs']:
                if PCCounter >= len(paths[pathID]):
                    continue

                if paths[pathID][PCCounter] == state.cpu.RIP:
                    newPathIDS.append(pathID)
                    keeping.append(str(pathID))

            state.context['pathIDs'] = newPathIDS

            if (not state.context['pathIDs']):  # No path includes the state state
                #print("Abandoning state with RIP=" + hex(state.cpu.RIP) + " PCCounter=" + str(PCCounter))
                state.abandon()


    #Extract jump targets
    def did_execute_instruction_callback(self, state, old_pc, new_pc, instruction):
        #This callback checks if we just executed the last instruction of a path.
        #If this is the case, we store the results in the variable "target" stored in the
        #global context.

        #Get the address we are looking for
        with self.manticore.locked_context() as context:
            paths = context['paths']

            #Check if we just executed the address we are looking for
            pathsEndingHere = []
            for i in range(0,len(paths)):
                if (len(paths[i])-1 == state.context['PCCounter'] and old_pc == paths[i][-1]):
                    pathsEndingHere.append(i)

            #Shorthand to make it easier to access the object
            targets = context['targets']

            if (len(pathsEndingHere) != 0):

                #Adding these two lines does, for some reason, make path 0 feasible..(Otherwise it is infeasible)
                #for i in pathsEndingHere:
                #    print("pathsEndingHere: " + str(i))

                #Calculate possible successors of the current instruction
                for concreteNewPC in state.solve_n(new_pc, nsolves=5):
                    for pathId in pathsEndingHere:
                        if pathId not in targets.keys():
                            targets[pathId] = set()
                        targets[pathId].add(hex(concreteNewPC))

                        # Log our results to stdout for debugging!
                        #out = hex(old_pc) + "->"
                        #out += ",".join([str(i) for i in targets[i]])
                        #print(out)


            # Put the results in the global context so that they can be accessed later (This is what sometimes seems to fail)
            context['targets'] = targets
