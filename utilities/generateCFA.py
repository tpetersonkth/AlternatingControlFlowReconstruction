import os, sys, time, networkx, angr
import queue

from angr.knowledge_plugins.cfg.cfg_node import CFGENode
from angrutils import plot_cfg

def main(file,outputDirectory):
    p = angr.Project(file,load_options={'auto_load_libs': False})
    basename = os.path.basename(file)

    print("Loading BBG from angr..")
    before = time.time()
    cfgEmulated = p.analyses.CFGEmulated()
    print("Obtained CFG from angr in " + str(time.time()-before) + " seconds")

    print("Outputting raw BBG manually in dot format")
    before = time.time()
    outputDot(outputDirectory + "/" + basename + "_cfg_manually.dot", basename, cfgEmulated.graph.nodes, cfgEmulated.graph.edges)
    print("Outputted raw BBG in " + str(time.time() - before) + " seconds")

    # Output resulting graph in a .dot file
    print("Outputting raw BBG using networkx")
    networkx.drawing.nx_pydot.write_dot(cfgEmulated.graph, outputDirectory + "/" + basename + "_cfg_angr.dot")

    print("Converting the BBG to a CFA")

    #Create a CFA from the BBG provided obtained with angr
    CFA = networkx.DiGraph()
    nodes = list(cfgEmulated.graph.nodes.keys())
    length = len(nodes)
    before = time.time()
    for i in range(length):
        sys.stdout.write("\r" + str(round(100*(i+1)/length,4))+"% in " + str(round(time.time() - before,2)) + " seconds  ")
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

    print("Outputting CCFA")
    before = time.time()
    basename = os.path.basename(file)
    outputDot(outputDirectory + "/" + basename + "_ccfa_angr.dot", basename ,CFA.nodes, CFA.edges, CFGENode=False)
    print("Outputted CCFA in " + str(time.time() - before) + " seconds")

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

def outputDot(file, basename, nodes, edges, CFGENode=True):
    fid = open(file, "w")
    fid.write(
        "digraph G {\nnode[shape=rectangle,style=filled,fillcolor=lightsteelblue,color=lightsteelblue]\nbgcolor=\"transparent\"\ngraph [label=\"Control flow from angr for " + basename + "\", labelloc=t, fontsize=35, pad=30]\n")

    for node in nodes:
        if (CFGENode):
            hexaddr = hex(node.addr)
        else:
            hexaddr = node
        fid.write("\"0x" + hexaddr + "\"[label = \"0x" + hexaddr + "\"];\n")

    for edge in edges:
        if (CFGENode):
            hexaddr1 = hex(edge[0].addr)
            hexaddr2 = hex(edge[1].addr)
        else:
            hexaddr1 = edge[0]
            hexaddr2 = edge[1]
        fid.write("\"0x" + hexaddr1 + "\" -> \"0x" + hexaddr2 + "\"[collor = \"#000000\"];\n")

    fid.write("}\n")
    fid.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 generateCFA.py [binary] [output directory]")
    else:
        main(sys.argv[1],sys.argv[2])
