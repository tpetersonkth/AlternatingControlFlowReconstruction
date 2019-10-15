'''
Author: Thomas Peterson
year: 2019
This script loads two graphs and calculates the coverage, soundness and precision based on these.
'''
import sys, networkx

def main(idealGraphFile, generatedGraphFile):
    IGraph = load(idealGraphFile)
    GGraph = load(generatedGraphFile)

    RICoverage, RISoundness, RIPrecision, TRICoverage, TRISoundness, TRIPrecision = calculateStats(IGraph,GGraph)

    #Build output
    out = ""
    out+="RI coverage: "+percentage(RICoverage)+"\n"
    out+="RI Soundness: "+percentage(RISoundness)+"\n"
    out+="RI Precision: "+percentage(RIPrecision)+"\n"
    out+="TRI Coverage: "+percentage(TRICoverage)+"\n"
    out+="TRI Soundness: "+percentage(TRISoundness)+"\n"
    out+="TRI Precision: "+percentage(TRIPrecision)+"\n"

    #Print stats to stdout
    print(out)

    #Write states to a file
    filename = generatedGraphFile.split(".")[0]
    fid = open(filename + "_graph_stats.dat","w")
    fid.write(out)
    fid.close()
    

def load(filename):
    graph = networkx.drawing.nx_pydot.read_dot(filename)
    return graph

def isTopNode(graph, node):
    # Jakstab colors nodes red if they are tops
    if 'fillcolor' in graph._node[node] and graph._node[node]['fillcolor'] == '"red"':
        return True
    return False

def calculateStats(idealGraph, graph):
    SizeOfTextSection=2**10#TODO: Load real size

    #Create reduced ideal graph
    reducedIdealGraph = networkx.MultiDiGraph()
    topEdgesCount = 0
    topNodes = []
    for node in graph.nodes:
        if node in idealGraph.nodes:
            reducedIdealGraph.add_node(node)
            # If top add all top edges to the counter
            if isTopNode(graph,node):
                topNodes.append(node)
                topEdgesCount += SizeOfTextSection

    #Add edges to reduced ideal graph and reduced top-free ideal graph
    topFreeReducedIdealGraph = reducedIdealGraph.copy()#Top free has the same nodes as the ideal graph but without top edges
    topEdges = []
    for edge in idealGraph.edges:
        if (edge[0] in reducedIdealGraph.nodes):
            if(edge[1] in reducedIdealGraph.nodes):
                reducedIdealGraph.add_edge(edge[0],edge[1])
            if (edge[0] not in topNodes):
                topFreeReducedIdealGraph.add_edge(edge[0],edge[1])
            else:
                topEdges.append(edge)

    #Add the targets of the top edges to the RIG
    for edge in topEdges:
        reducedIdealGraph.add_node(edge[1])
        reducedIdealGraph.add_edge(edge[0],edge[1])

    GE = set(graph.edges)
    RIGE = set(reducedIdealGraph.edges)
    TRIGE = set(topFreeReducedIdealGraph.edges)

    # Calculate coverage, soundness and precision with respect to the reduced ideal graph
    intersecting = float(len(GE.intersection(RIGE)))
    RICoverage = intersecting / len(RIGE) if len(RIGE) != 0 else None
    RISoundness = intersecting / len(GE) if len(GE) != 0 else None
    RIPrecision = 1 / 2 * (intersecting / len(RIGE) + intersecting / len(GE)) if (len(GE) != 0 and len(RIGE) != 0) else None

    # Calculate coverage, soundness and precision with respect to the reduced top-free ideal graph
    intersecting = float(len(GE.intersection(TRIGE)))
    TRICoverage = intersecting / len(TRIGE) if len(TRIGE) != 0 else None
    TRISoundness = intersecting / len(GE) if len(GE) != 0 else None
    TRIPrecision = 1 / 2 * (intersecting / len(TRIGE) + intersecting / len(GE)) if (len(GE) != 0 and len(TRIGE) != 0) else None

    return (RICoverage, RISoundness, RIPrecision, TRICoverage, TRISoundness, TRIPrecision)

'''
Calculate coverage, soundness, precision and precision error without compensating for tops or only considering the subgraph of the ideal graph
'''
def calculateStatsRaw(idealGraph, graph):
    GE = set(graph.edges)
    IGE = set(idealGraph.edges)

    #Calculate coverage and soundnes
    intersecting = float(len(GE.intersection(IGE)))
    coverage = intersecting/len(IGE) if len(IGE) != 0 else None
    soundness = intersecting/len(GE) if len(GE) != 0 else None
    
    #Calculate precision
    precision = 1/2*(intersecting/len(IGE) + intersecting/len(GE)) if (len(GE) != 0 and len(IGE) != 0) else None

    #Calculate precision error
    IminG = IGE - GE
    GminI = GE - IGE 
    precisionError = 1/2*(len(IminG)/len(IGE) + len(GminI)/len(GE)) if (len(GE) != 0 and len(IGE) != 0) else None

    return (coverage, soundness, precision, precisionError)

def percentage(decimalForm):
    if (decimalForm == None):
        return "-"

    return str(round(100*decimalForm,2))+"%"

if __name__ == "__main__":
    if (len(sys.argv) < 3):
        print("Usage: Python3 calculateStats [Path to ideal graph] [Path to generated graph]")
    else:
        main(sys.argv[1],sys.argv[2])
        
    
