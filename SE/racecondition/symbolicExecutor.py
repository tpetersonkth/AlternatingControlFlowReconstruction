from manticore.native import Manticore
from customPlugins import DirectedExtractorPlugin

def executeDirected(program, paths):
    #Program is a string to a binary to analyze
    #Paths is a list of lists where each list contains a sequence of integers representing addresses of instructions in the binary

    m = Manticore(program)

    #Store variables in global context to ensure that we can communicate them to the callback function
    with m.locked_context() as context:
        #We store the paths in the context to make them accessible in the plugin
        context['paths'] = paths
        context['targets'] = dict()

        #Register the plugin for callbacks(So it is called before and after executing instructions)
        m.register_plugin(DirectedExtractorPlugin())

    #Execute manticore which will do a directed symbolic execution following the paths in the paths variable
    m.run()

    #Print the successors of the last instructions of each path
    with m.locked_context() as context:
        targets = context['targets']

        for i in range(len(paths)):
            if i in targets.keys():
                print("Path " + str(i) + "[len=" + str(len(paths[i])) + "] ending with " + hex(
                    paths[i][-1]) + " has the following successors " +
                      ",".join([str(i) for i in targets[i]]))
            else:
                print("Path " + str(i) + "[len=" + str(len(paths[i])) + "]" + " is infeasible")

    #Return the successors of the last instruction in each path
    return targets

def formatPath (p):
    #Chops a path string into a list of integers
    p = p.split(",")
    p = [int(i, 16) for i in p]
    return p

if __name__ == "__main__":

    p1 = formatPath('0x08048080,0x08048085,0x0804808a,0x0804808f,0x08048094,0x08048096,0x0804809d,0x080480a2,0x080480a4,0x080480cc')
    p2 = formatPath('0x08048080,0x08048085,0x0804808a,0x0804808f,0x08048094,0x08048096,0x0804809d,0x080480a2,0x080480ae,0x080480b8,0x080480ba,0x080480bf,0x080480c4,0x080480c9,0x080480cb')

    #Should return that 0x080480cc has the successor 0x80480a9 and that 0x080480cb has the successor 0x80480b3 (However, sometimes returns that p1 is infeasible and thus that 0x080480cc has no successors)
    executeDirected("doubleCallRet",[p1,p2])