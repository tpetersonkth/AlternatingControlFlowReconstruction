import os, sys, networkx, angr

from angrutils import plot_cfg

def main(file,outputDirectory):
    p = angr.Project(file,load_options={'auto_load_libs': False})
    #cfg = p.analyses.CFGFast()
    cfgEmulated = p.analyses.CFGEmulated()

    basename = os.path.basename(file)

    plot_cfg(cfgEmulated, os.path.abspath(outputDirectory+"/"+basename))
    networkx.readwrite.edgelist.write_weighted_edgelist(cfgEmulated.graph, os.path.abspath(outputDirectory+"/"+basename+".nx"), delimiter=",")

    #G = networkx.grid_2d_graph(5, 5)  # 5x5 grid
    networkx.drawing.nx_pydot.write_dot(cfgEmulated.graph, "grid.dot")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Len:"+str(len(sys.argv)))
        print("Usage: python3 generateCFG.py [binary] [directory for CFG]")
    else:
        main(sys.argv[1],sys.argv[2])