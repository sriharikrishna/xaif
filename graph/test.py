#!/usr/bin/env python
from xaifGraph import XAIFGraph, XAIFVertex
from xaifParser import XAIFParser, XAIFContentHandler

graph = XAIFGraph()
vertices = []
for i in range(0,9):
  vertices.append(XAIFVertex(str(i)))
    
for v in vertices:
  graph.addVertex(v)
        
graph.addEdges(vertices[0],[vertices[1],vertices[2]],[vertices[2],vertices[3]])
graph.addEdges(vertices[2],[vertices[6],vertices[4]],[vertices[2],vertices[5]])
graph.annotateEdge(vertices[0], vertices[1], vertices[2])
graph.annotateEdge(vertices[4], vertices[5], vertices[3])

#print graph
#graph.display()

parser = XAIFParser()
#parser.validate("uwe_ex_1.xaif")
parser.parse("../schema/examples/uwe_ex_1.xaif")
parser.displayGraph()
  
