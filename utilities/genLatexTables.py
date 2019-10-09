# This is a file to generate latex tables from result files of the genResults.sh script(Files ending with .dat).

import os, sys

def main():
    stats = dirToStats(sys.argv[1])
    t1 = generateTable(stats,["Coverage","Precision","soundness","Unresolved Tops","Tops"])
    t2 = generateTable(stats,["Total time", "CPA time","DFS time", "DSE time"])

    print(t1)
    print(t2)

def generateTable(stats, fields):
    columns = len(fields) + 2# + 2 for name of binary and mode
    out = ""
    out += "\\begin{table}[ht]\n"
    out += "\\centering\n"
    out += "\scalebox{0.7}{\n"
    out += "\\begin{tabular}{"+"l".join("|"*(columns+2))+"}\n"
    out += "\\hline\n"

    bfFields = ["\\textbf{File}","\\textbf{Mode}"]
    bfFields = bfFields + ["\\textbf{"+field+"}" for field in fields]
    out += " & ".join(bfFields) + "\\\\ \hline \n"

    sortedValues = []
    for binary in stats.keys(): 
        for analysis in stats[binary].keys():
            values = ["".join([char for char in binary if not char.isdigit()]), analysis]
            for field in fields:
                values.append(stats[binary][analysis][field].replace("%","\%"))
            sortedValues.append(values)

    modeEnum = {"c":0,"cD":1,"i":2,"iD":3}
    sortedValues.sort(key = lambda values: (values[0],modeEnum[values[1]]))

    for values in sortedValues:
        out += " & ".join(values) + "\\\\ \hline\n"

    out += "\\end{tabular}\n"
    out += "}\n"
    out += "\\caption[]{}\n"
    out += "\\label{tab:unnamed}\n"
    out += "\\end{table}\n"

    return out

'''
    dirToStats(directory) - Generates a stats object from a directory
    Params: 
        directory - A directory to retrieve stats from
    Returns: 
        stats - A stats object containing the stats of the provided directory
'''
def dirToStats(directory):
    print("Reading from directory: "+directory)
    stats = {}

    for f in os.listdir(directory):
        if (f.endswith("stats.dat") or f.endswith("ccfa_graph_stats.dat")):
            addStats(stats, os.path.join(directory,f))
    
    return stats

'''
    addStats(stats, filename) - Adds the content of a file to a stats dictionary
    Params:
        stats - Dictionary of stats to fill
        filename - Path to a file of the format [binaryName]_[analysis type]_*.dat 

'''
def addStats(stats, filename):
    fid = open(filename,"r")
    lines = fid.readlines()
    basename = os.path.basename(filename)

    basename = basename.split("_")
    analysisType = basename[1]
    basename = basename[0]

    # Initialize stats for this file
    if basename not in stats.keys():
        stats[basename] = dict()
    if analysisType not in stats[basename].keys():
        stats[basename][analysisType] = dict()

    # Fill the stats of this file in the dictionary
    for line in lines:
        if ":" in line: 
            line = line.split(":")
            stats[basename][analysisType][line[0].strip()] = line[1].strip()



if __name__ == "__main__":
    main()