from manticore.native import Manticore
from customPlugins import ACFRPlugin

#TODO: Use logger
#TODO: Purely symbolic execution?
#TODO: Multiple target addresses

def execute(program, address):
    #m = Manticore(program, pure_symbolic=True)
    m = Manticore(program, pure_symbolic=False)

    #Store variables in global context to ensure that we can communicate them to the callback function
    with m.locked_context() as context:
        context['instructionAddress'] = address
        context['targets'] = set()

    #Register hook to have each executed instruction's RIP printed to the command line
    m.add_hook(None, print_ip)
    m.register_plugin(ACFRPlugin())

    m.run()
    with m.locked_context() as context:
        targets = context['targets']

    print("Run finished")
    print("Determined that the instruction at " + hex(address) + " can jump to the following addresses: " + ",".join(targets))

def executeDirected(program, address, paths, pathslen):
    #m = Manticore(program, pure_symbolic=True)
    m = Manticore(program, pure_symbolic=False)

    #Store variables in global context to ensure that we can communicate them to the callback function
    with m.locked_context() as context:
        context['instructionAddress'] = address
        context['targets'] = set()

    #Register hook to have each executed instruction's RIP printed to the command line
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


#Prints the RIP of a state
def print_ip(state):
    print(hex(state.cpu.RIP))