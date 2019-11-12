"""
Author: Thomas Peterson
Year: 2019
"""

class PathObject():
    path = []#List of addresses
    pathLen = 0
    def __init__(self,path,id):
        self.path = path
        self.pathLen = len(path)
        self.pathID = id