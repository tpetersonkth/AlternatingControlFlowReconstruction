from manticore.core.plugin import Plugin

#A plugin to extract the successor instructions of a given instruction and to direct execution along a set of predefined paths
class ACFRPlugin(Plugin):
    def will_execute_instruction_callback(self, state, pc, instruction):
        #Directed execution
        pass

    def did_execute_instruction_callback(self, state, old_pc, new_pc, instruction):
        #Extract jump targets

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