'''
Author: Thomas Peterson
year: 2019
This file loads two graphs and calculates the coverage, soundness, precision and precision error based on these. 
'''
import sys, networkx

def main(idealGraphFile, generatedGraphFile):
    IGraph = load(idealGraphFile)
    GGraph = load(generatedGraphFile)

    coverage, soundness, precision, precisionError = calculateStats(IGraph,GGraph)

    #Build output
    out = ""
    out+="Coverage: "+percentage(coverage)+"\n"
    out+="soundness: "+percentage(soundness)+"\n"
    out+="Precision: "+percentage(precision)+"\n"
    out+="Precision error: "+percentage(precisionError)+"\n"

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

def calculateStats(idealGraph, graph):
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
        
    
