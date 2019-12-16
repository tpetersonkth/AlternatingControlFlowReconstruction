"""
Author: Thomas Peterson
Year: 2019
"""

#An object which stores a set of paths
class PathsObject():
    paths = []#List of PathObjects
    pathsLen = 0
    targets = []#List of target addresses to resolve
    def __init__(self,pathObjects):
        self.paths = pathObjects
        self.pathsLen = len(pathObjects)
        self.lastAddresses = []#The last address of a path is the address of the instruction we want to determine successors for
        for i in range(self.pathsLen):
            self.lastAddresses.append(self.paths[i].path[self.paths[i].pathLen-1])
