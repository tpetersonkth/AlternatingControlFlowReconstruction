'''
Author: Thomas Peterson
year: 2019
This script loads two graphs and calculates the coverage, soundness and precision based on these.
'''
import sys, os, networkx

from presentStats import addStats

def main(idealGraphFile, generatedGraphFile, statsfile):
    IGraph = load(idealGraphFile)
    GGraph = load(generatedGraphFile)

    stats = {}
    addStats(stats,statsfile)

    basename = os.path.basename(statsfile)
    basename = basename.split("_")
    analysisType = basename[1]
    basename = basename[0]

    textSectionSize = int(stats[basename][analysisType]['Section .text size'],16)

    Coverage, Soundness, Precision, TFCoverage, TFSoundness, TFPrecision = calculateStats(IGraph,GGraph,textSectionSize)

    #Build output
    out = ""
    out+="Coverage: "+percentage(Coverage)+"\n"
    out+="Soundness: "+percentage(Soundness)+"\n"
    out+="Precision: "+percentage(Precision)+"\n"
    out+="Top free coverage: "+percentage(TFCoverage)+"\n"
    out+="Top free soundness: "+percentage(TFSoundness)+"\n"
    out+="Top free precision: "+percentage(TFPrecision)+"\n"

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

# Calculate coverage, soundness and precision with respect to the ideal graph
def calculateStats(idealGraph, graph, SizeOfTextSection):

    topFreeGraph, topNodes, _ = getTopFreeGraph(graph)
    topFreeIdealGraph, _, idealTopEdges = getTopFreeGraph(idealGraph, providedTopNodes=topNodes)

    # Convert to sets to perform set operations in the calculations
    TFGE = set(topFreeGraph.edges)
    TFIGE = set(topFreeIdealGraph.edges)
    idealTopEdges = set(idealTopEdges)
    numberOfTopEdgesOfGraph = SizeOfTextSection*len(topNodes)

    #Every edge from a top node in the ideal graph is covered since a top node points to every byte in the .text section
    intersectingTopEdges = len(idealTopEdges)
    intersecting = float(len(TFGE.intersection(TFIGE))+intersectingTopEdges)

    #Calculate metrics
    Coverage = intersecting / len(idealGraph.edges) if len(idealGraph.edges) != 0 else None
    Soundness = intersecting / (len(TFGE)+numberOfTopEdgesOfGraph) if (len(TFGE)+numberOfTopEdgesOfGraph) != 0 else None
    Precision = 1 / 2 * (Soundness + Coverage) if (Coverage != None and Soundness != None) else None

    # Top free graphs can be handled as regular graphs
    TFCoverage, TFSoundness, TFPrecision = calculateStatsRaw(idealGraph,topFreeGraph)

    return (Coverage, Soundness, Precision, TFCoverage, TFSoundness, TFPrecision)

'''
Calculate coverage, soundness, precision and precision error without compensating for tops
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
    #IminG = IGE - GE
    #GminI = GE - IGE
    #precisionError = 1/2*(len(IminG)/len(IGE) + len(GminI)/len(GE)) if (len(GE) != 0 and len(IGE) != 0) else None

    return (coverage, soundness, precision)

def percentage(decimalForm):
    if (decimalForm == None):
        return "-"

    return str(round(100*decimalForm,2))+"%"

if __name__ == "__main__":
    if (len(sys.argv) < 4):
        print("Usage: Python3 calculateStats [Path to ideal graph] [Path to generated graph] [Path to statsfile]")
    else:
        main(sys.argv[1],sys.argv[2],sys.argv[3])
        
    
