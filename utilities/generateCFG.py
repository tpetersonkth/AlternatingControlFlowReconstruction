import os, sys, networkx, angr
from angrutils import plot_cfg

def main(file,outputDirectory):
    p = angr.Project(file,load_options={'auto_load_libs': False})
    #cfg = p.analyses.CFGFast()
    cfgEmulated = p.analyses.CFGEmulated()

    basename = os.path.basename(file)

    plot_cfg(cfgEmulated, os.path.abspath(outputDirectory+"/"+basename), asminst=True, remove_imports=True, remove_path_terminator=True)
    networkx.readwrite.edgelist.write_weighted_edgelist(cfgEmulated.graph, os.path.abspath(outputDirectory+"/"+basename+".nx"), delimiter=",")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Len:"+str(len(sys.argv)))
        print("Usage: python3 angrGenerateCFG.py [binary] [directory for CFG]")
    else:
        main(sys.argv[1],sys.argv[2])