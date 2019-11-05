'''
Author: Thomas Peterson
year: 2019
This script loads two graphs and calculates the accuracy, soundness and precision based on these.
'''

import sys, os, networkx, datetime
from presentStats import addStats

def main(idealGraphFile, generatedGraphFile, statsfile):
    #Load graphs
    tprint("Loading ideal graph")
    IGraph = load(idealGraphFile)
    tprint("Loading generated graph")
    GGraph = load(generatedGraphFile)
    tprint("Graphs loaded")

    #Load stats
    stats = {}
    addStats(stats, statsfile)

    #Get basename
    basename = os.path.basename(statsfile)
    basename = basename.split("_")
    analysisType = basename[1]
    basename = basename[0]

    #Get text section size from stats object
    textSectionSize = int(stats[basename][analysisType]['Section .text size'],16)

    #Calculate graph stats
    tprint("Starting calculations of graph stats")
    accuracy, soundness, precision, TFAccuracy, TFSoundness, TFPrecision = calculateStats(IGraph,GGraph,textSectionSize)

    #Print stats to stdout
    out = "\n"
    out+="Accuracy: "+percentage(accuracy)+"\n"
    out+="Soundness: "+percentage(soundness)+"\n"
    out+="Precision: "+percentage(precision)+"\n"
    out+="Top Free Accuracy: "+percentage(TFAccuracy)+"\n"
    out+="Top Free Soundness: "+percentage(TFSoundness)+"\n"
    out+="Top Free Precision: "+percentage(TFPrecision)+"\n"
    print(out)

    #Write stats to a file
    filename = generatedGraphFile.split(".")
    filename[-2] += "_graph_stats.dat"
    filename = ".".join(filename[:-1])
    tprint("Writing graph stats to " + filename)
    fid = open(filename,"w")
    fid.write(out)
    fid.close()

'''
Loads a graph from a file
Params:
    filename - A path to a .dot file
Returns:
    A networkx graph object corresponding to the graph in the file specified by filename
'''
def load(filename):
    graph = networkx.drawing.nx_pydot.read_dot(filename)
    return graph

'''
Checks if a node is a top node
Params: 
    graph - A graph which contains the node
    node - A node in the graph
Returns:
    True if the node is a top node, False otherwise
'''
def isTopNode(graph, node):
    # Jakstab colors nodes red if they are tops
    if 'fillcolor' in graph._node[node] and graph._node[node]['fillcolor'] == '"red"':
        return True
    return False

'''
Converts a top graph into a graph without edges from top locations
Params:
    graph - The graph to convert into a top-free form
    providedTopNodes(Opt) - A list of nodes which will be treated like top locations
Returns: 
    A graph that contains all edges of the graph graph except does who originate from a top location
'''
def getTopFreeGraph(graph, providedTopNodes=[]):
    topFreeGraph = networkx.MultiDiGraph()  # Top free has the same nodes as the ideal graph but without top edges
    topNodes = []
    for node in graph.nodes:
        topFreeGraph.add_node(node)
        # If top add all top edges to the counter
        if isTopNode(graph, node):
            topNodes.append(node)

    topNodes = topNodes + providedTopNodes

    topEdges = []
    for edge in graph.edges:

        # If this edge is not a top edge
        if (edge[0] not in topNodes):
            topFreeGraph.add_edge(edge[0], edge[1])
        else:
            topEdges.append(edge)

    return topFreeGraph, topNodes, topEdges

'''
Calculate accuracy, soundness and precision with respect to an ideal graph
Params:
    idealGraph - The graph which is the ground truth
    graph - The graph to evaluate with respect to the ground truth
    sizeOfTextSection - The size of the text section (Required for calulating the number of edges from a top node)
Returns: The accuracy, soundness, precision, TFAccuracy, TFSoundness, TFPrecision of the graph graph with respect to the graph idealGraph
'''
def calculateStats(idealGraph, graph, sizeOfTextSection):

    tprint("Generating top free graph")
    topFreeGraph, topNodes, _ = getTopFreeGraph(graph)
    tprint("Generating top free ideal graph")
    topFreeIdealGraph, _, idealTopEdges = getTopFreeGraph(idealGraph, providedTopNodes=topNodes)
    tprint("Done generating top free graphs")

    # Convert to sets where nodes are integers to perform set operations in the calculations
    TFGE = set([(int(i[0],16),int(i[1],16)) for i in topFreeGraph.edges])
    TFIGE = set([(int(i[0],16),int(i[1],16)) for i in topFreeIdealGraph.edges])
    idealTopEdges = set(idealTopEdges)
    numberOfTopEdgesOfGraph = sizeOfTextSection*len(topNodes)

    tprint("ideal graph top edges: ")
    for e in idealTopEdges:
        print(e)

    #Every edge from a top node in the ideal graph is covered since a top node points to every byte in the .text section
    intersectingTopEdges = len(idealTopEdges)
    intersecting = float(len(TFGE.intersection(TFIGE))+intersectingTopEdges)

    tprint("Intersecting: " + str(intersecting))
    tprint("Intersecting Top Edges: " + str(intersectingTopEdges))

    print("")

    #Calculate metrics
    soundness = intersecting / len(idealGraph.edges) if len(idealGraph.edges) != 0 else None
    accuracy = intersecting / (len(TFGE)+numberOfTopEdgesOfGraph) if (len(TFGE)+numberOfTopEdgesOfGraph) != 0 else None
    precision = 1 / 2 * (soundness + accuracy) if (accuracy != None and soundness != None) else None

    # Top free graphs can be handled as regular graphs
    TFAccuracy, TFSoundness, TFPrecision = calculateStatsRaw(idealGraph,topFreeGraph)

    return (accuracy, soundness, precision, TFAccuracy, TFSoundness, TFPrecision)

'''
Calculate accuracy, soundness and precision without compensating for tops
Params:
    idealGraph - The graph which is the ground truth
    graph - The graph to evaluate with respect to the ground truth
Returns: The accuracy, soundness, precision of the graph graph with respect to the graph idealGraph
'''
def calculateStatsRaw(idealGraph, graph):
    #Convert graph edges into to a set of tuples of integers corresponding to the two nodes of the edge
    GE = set([(int(i[0],16),int(i[1],16)) for i in graph.edges])
    IGE = set([(int(i[0],16),int(i[1],16)) for i in idealGraph.edges])

    #Calculate accuracy and soundnes
    intersecting = float(len(GE.intersection(IGE)))
    soundness = intersecting/len(IGE) if len(IGE) != 0 else None
    accuracy = intersecting/len(GE) if len(GE) != 0 else None

    #Calculate precision
    precision = 1/2*(intersecting/len(IGE) + intersecting/len(GE)) if (len(GE) != 0 and len(IGE) != 0) else None

    #Calculate precision error
    #IminG = IGE - GE
    #GminI = GE - IGE
    #precisionError = 1/2*(len(IminG)/len(IGE) + len(GminI)/len(GE)) if (len(GE) != 0 and len(IGE) != 0) else None

    return (accuracy, soundness, precision)

'''
Converts a real from decimal form to its corresponding percentage
Params:
    decimalForm - The number in decimal form
Returns:
    The corresponding percentage
'''
def percentage(decimalForm):
    if (decimalForm == None):
        return "-"

    return str(100*decimalForm)+"%"

'''
Print a message to stdout with a timestamp
Params:
    message - The message to print
'''
def tprint(message):
    print(str(datetime.datetime.now())+": "+str(message))

if __name__ == "__main__":
    if (len(sys.argv) < 4):
        print("Usage: Python3 calculateStats [Path to ideal graph] [Path to generated graph] [Path to statsfile]")
    else:
        main(sys.argv[1],sys.argv[2],sys.argv[3])
