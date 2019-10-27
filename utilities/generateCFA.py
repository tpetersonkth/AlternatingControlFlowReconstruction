import os, sys, networkx, angr
import queue

from angr.knowledge_plugins.cfg.cfg_node import CFGENode
from angrutils import plot_cfg

def main(file,outputDirectory):
    p = angr.Project(file,load_options={'auto_load_libs': False})
    basename = os.path.basename(file)

    print("Loading BBG from angr..")
    cfgEmulated = p.analyses.CFGEmulated()

    print("Outputting raw BBG manually in dot format")
    fid = open(outputDirectory + "/" + basename + "_cfg_manually.dot", "w")
    fid.write("digraph G {\nnode[shape=rectangle,style=filled,fillcolor=lightsteelblue,color=lightsteelblue]\nbgcolor=\"transparent\"\ngraph [label=\"CFG from angr for " + basename + "\", labelloc=t, fontsize=35, pad=30]\n")

    for node in cfgEmulated.graph.nodes:
        fid.write("\"0x"+hex(node.addr)+"\"[label = \"0x"+hex(node.addr)+"\"];\n")

    for edge in cfgEmulated.graph.edges:
        fid.write("\"0x" + hex(edge[0].addr) + "\" -> \"0x" + hex(edge[1].addr) + "\"[collor = \"#000000\"];\n")

    fid.write("}\n")
    fid.close()

    # Output resulting graph in a .dot file
    print("Outputting raw BBG using networkx")
    networkx.drawing.nx_pydot.write_dot(cfgEmulated.graph, outputDirectory + "/" + basename + "_cfg_angr.dot")

    print("Converting the BBG to a CFA")

    #Create a CFA from the BBG provided obtained with angr
    CFA = networkx.DiGraph()
    nodes = list(cfgEmulated.graph.nodes.keys())
    length = len(nodes)
    for i in range(length):
        sys.stdout.write("\r" + str(round(100*i/length,4))+"%")
        sys.stdout.flush()

        node = nodes[i]
        if (node.is_simprocedure):
            continue

        CFA.add_node(hex(node.addr))

        prev = None
        for blockNode in node.instruction_addrs:
            CFA.add_node(hex(blockNode))
            if (prev != None):
                CFA.add_edge(hex(prev),hex(blockNode))
            prev = blockNode

        #Prev will now be the last instruction in the block
        last = prev
        if (last == None):
            last = node.addr

        #Add edges from last instruciton in each block to the entry of suceeding blocks
        successors = getNonSimprocedureSuccessors(node)
        for successor in successors:
            CFA.add_edge(hex(last),hex(successor.addr))

    #Output resulting graph in a .dot file
    sys.stdout.write("\n")
    print("Outputting CFA")
    basename = os.path.basename(file)
    networkx.drawing.nx_pydot.write_dot(CFA, outputDirectory + "/" + basename + "_ccfa_angr.dot")

    #Illustrate the BBG as a PNG
    #plot_cfg(cfgEmulated, os.path.abspath(outputDirectory+"/"+basename))

    #Export the CFA as a networkx edgelist
    #networkx.readwrite.edgelist.write_weighted_edgelist(CFA, os.path.abspath(outputDirectory+"/"+basename+".nx"), delimiter=",")

#Returns the set of all successors that are not simprocedures
#Note that it skips every simprocedure node until a non-simprocedure node is found
def getNonSimprocedureSuccessors(node):
    visited = [node.addr]
    answer = []
    worklist = queue.Queue()
    worklist.put(node)
    while not worklist.empty():
        node = worklist.get()
        for s in node.successors:
            if not s.is_simprocedure:
                answer.append(s)
            else:
                if(s.addr not in visited):
                    visited.append(s.addr)
                    worklist.put(s)
    return answer

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 generateCFA.py [binary] [output directory]")
    else:
        main(sys.argv[1],sys.argv[2])
