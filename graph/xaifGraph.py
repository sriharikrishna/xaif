from __future__ import generators
import types

class XAIFVertex (object):
  def __init__(self, id='-1', type='NoType'):
    self.id = id
    self.type = type
    self.attr = {}
    self.__level = 0
    return
 
  def __str__(self):
    return 'vertex <%s:%s:%s>' % (self.type, self.id, self.attr)

  def getAttributes(self):
    return self.attr
  
  def setAttributes(self, names, attrs):
    ''' names: string list
    attrs: xml.sax attribute structure, must have get(name) method'''
    for attr_name in names:
      self.attr[attr_name] = attrs.get(attr_name)
    return

  def getId(self):
    return self.id
  def setId(self, id):
    self.id = id
    return

  def getType(self):
    return self.type
  def setType(self, type):
    self.type = type
    return

  def getLevel(self):
    return self.__level
  def setLevel(self, lev=0):
    self.__level = lev
    return
  def incrementLevel(self):
    self.__level = self.__level + 1
    return self.__level

class XAIFEdge(object):
  def __init__(self, id, src, tgt):
    self.id = id
    self.source = src
    self.target = tgt
    return

  def __str__(self):
    return 'id: %s, source: %s, target: %s' % (self.id, self.source, self.target)

  def getSource(self):
    return self.source
  def setSource(self, srcvertex):
    self.source = srcvertex
    return

  def getTarget(self):
    return self.target
  def setTarget(self, tgtvertex):
    self.target = tgtvertex
    return

class XAIFGraph(object):
  def __init__(self, vertices = {}):
    '''Create a graph'''
    self.vertices = {}
    '''Edges are dictionaries with start vertex keys, and values that are dictionaries
       whose keys are the target vertex keys and values are pointer to vertices.
       For example, edge[v1][v2] is the data (or label) of the edge from v1 to v2'''
    self.inEdges  = {}
    self.outEdges = {}
    self.roots = []
    self.leaves = []
    map(self.addVertex, vertices)
    self.attr = {}
    return

  def __str__(self):
    return 'XAIFGraph with '+str(len(self.vertices))+' vertices and '+str(reduce(lambda k,l: k+l, [len(edgeList) for edgeList in self.inEdges.values()], 0))+' edges'

  def getAttributes(self):
    return self.attr
  
  def setAttributes(self, names, attrs):
    ''' names: string list
    attrs: xml.sax attribute structure, must have get(name) method'''
    for attr_name in names:
      self.attr[attr_name] = attrs.get(attr_name)
    return

  def addVertex(self, vertex):
    '''Add a vertex if it does not already exist in the vertex list
       - Should be able to use Set in Python 2.3'''
    if vertex is None: return
    if not vertex.getId() in self.vertices.keys():
      self.vertices[vertex.getId()] = vertex
      self.clearEdges(vertex)
    return

  def addEdge(self, edge):
    '''Add an XAIFEdge to the graph'''
    src = self.vertices[edge.getSource()]
    tgt = self.vertices[edge.getTarget()]
    if not src in self.inEdges[tgt].keys(): self.inEdges[tgt][src] = None
    if not tgt in self.outEdges[src].keys(): self.outEdges[src][tgt] = None
    return
  
  def addEdges(self, vertex, inputs = [], outputs = []):
    '''Define the in and out edges for a vertex by listing the other vertices defining the edges
       - If any vertex does not exist in the graph, it is created'''
    self.addVertex(vertex)
    for input in inputs:
      self.addVertex(input)
      if not vertex is None and not input is None:
        if not input  in self.inEdges[vertex]: self.inEdges[vertex][input] = None
        if not vertex in self.outEdges[input]: self.outEdges[input][vertex] = None
    for output in outputs:
      self.addVertex(output)
      if not vertex is None and not output is None:
        if not vertex in self.inEdges[output]:  self.inEdges[output][vertex] = None
        if not output in self.outEdges[vertex]: self.outEdges[vertex][output] = None
    return

  def getEdges(self, vertex):
    '''vertex is of type XAIFVertex'''
    return (self.inEdges[vertex], self.outEdges[vertex])

  def clearEdges(self, vertex):
    self.inEdges[vertex]  = {}
    self.outEdges[vertex] = {}
    return

  def annotateEdge(self, srcVertex, tgtVertex, data = None):
    self.addVertex(srcVertex)
    self.addVertex(tgtVertex)
    self.addEdges(srcVertex,[],[tgtVertex])
    self.outEdges[srcVertex][tgtVertex] = data
    self.inEdges[tgtVertex][srcVertex] = data
    return

  def clearEdgeAnnotations(self, srcVertex, tgtVertex):
    self.outEdges[srcVertex][tgtVertex] = None
    self.inEdges[tgtVertex][srcVertex] = None
    return

  def getEdgeData(self, srcVertex, tgtVertex):
    return self.outEdges[srcVertex][tgtVertex]

  def removeVertex(self, vertex):
    '''Remove a vertex if already exists in the vertex list
       - Also removes all associated edges'''
    if vertex is None: return
    if vertex in self.vertices:
      self.vertices.remove(vertex)
      del self.inEdges[vertex]
      del self.outEdges[vertex]
      for v in self.vertices:
        if vertex in self.inEdges[v]:  self.inEdges[v].remove(vertex)
        if vertex in self.outEdges[v]: self.outEdges[v].remove(vertex)
    return

  def addSubgraph(self, graph):
    '''Add the vertices and edges of another graph into this one'''
    map(self.addVertex, graph.vertices)
    map(lambda v: apply(self.addEdges, (v,)+graph.getEdges(v)), graph.vertices)
    return

  def removeSubgraph(self, graph):
    '''Remove the vertices and edges of a subgraph, and all the edges connected to it'''
    map(self.removeVertex, graph.vertices)
    return

  def printIndent(self, indent):
    import sys
    for i in range(indent): sys.stdout.write('  ')

  def display(self):
    print 'I am a XAIFGraph with '+str(len(self.vertices))+' vertices'
    for vertex in self.vertices:
      print 'vertex ', vertex, 'in: ' + str(map(self.vertices.index, self.inEdges[vertex])) +' out: '+str(map(self.vertices.index, self.outEdges[vertex]))
      print '  inEdges: '
      print '    ' + str(self.inEdges[vertex])
      print '  outEdges: '
      print '    ' + str(self.outEdges[vertex])
    return
  
  def displaySorted(self):
    #print 'I am an XAIFGraph with '+str(len(self.vertices))+' vertices'
    print 'BreadthFirstSearch:'
    for vertex in XAIFGraph.breadthFirstSearch(self,1):
      self.printIndent(vertex.getLevel())
      inedges, outedges = [], []
      for v in self.inEdges[vertex]: inedges.append(str(v))
      for v in self.outEdges[vertex]: outedges.append(str(v))
      print vertex, ' in: ', inedges, ' out: ', outedges

##    print '\nDepthFirstSearch:'
##    for vertex in XAIFGraph.depthFirstSearch(self, 1):
##      self.printIndent(vertex.getLevel())
##      inedges, outedges = [], []
##      for v in self.inEdges[vertex]: inedges.append(str(v))
##      for v in self.outEdges[vertex]: outedges.append(str(v))
##      print vertex, ' in: ', inedges, ' out: ', outedges
      #print '('+str(self.vertices.index(vertex))+') '+str(vertex)+' in: '+str(map(self.vertices.index, self.inEdges[vertex]))+' out: '+str(map(self.vertices.index, self.outEdges[vertex]))
    return

  def appendGraph(self, graph):
    '''Join every leaf of this graph to every root of the input graph, leaving the result in this graph'''
    leaves = XAIFGraph.getLeaves(self)
    self.addSubgraph(graph)
    map(lambda v: self.addEdges(v, outputs = XAIFGraph.getRoots(graph)), leaves)
    return self

  def prependGraph(self, graph):
    '''Join every leaf of the input graph to every root of this graph, leaving the result in this graph'''
    roots = XAIFGraph.getRoots(self)
    self.addSubgraph(graph)
    map(lambda v: self.addEdges(v, outputs = roots), XAIFGraph.getLeaves(graph))
    return self

  def getRoots(graph):
    '''Return all the sources in the graph (nodes without entering edges)'''
    graph.roots = []
    for i in graph.vertices.keys():
      v = graph.vertices[i]
      if not len(graph.getEdges(v)[0]):
        graph.roots.append(v)
    return graph.roots
    #return filter(lambda v: not len(graph.getEdges(v)[0]), graph.vertices)
  getRoots = staticmethod(getRoots)

  def getLeaves(graph):
    '''Return all the sinks in the graph (nodes without exiting edges)'''
    graph.leaves = []
    for i in graph.vertices.keys():
      v = graph.vertices[i]
      if not len(graph.getEdges(v)[1]):
        graph.leaves.append(v)
    return graph.leaves
    #return filter(lambda v: not len(graph.getEdges(v)[1]), graph.vertices)
  getLeaves = staticmethod(getLeaves)

  def depthFirstVisit(graph, vertex, seen = None, returnFinished = 0):
    '''This is a generator returning vertices in a depth-first traversal only for the subtree rooted at vertex'''
    if seen is None: seen = []
    seen.append(vertex)
    if not returnFinished:
      yield vertex
    for v in graph.getEdges(vertex)[1]:
       if not v in seen:
        try:
          for v2 in XAIFGraph.depthFirstVisit(graph, v, seen, returnFinished):
            yield v2
        except StopIteration:
          pass
    if returnFinished:
      yield vertex
    return
  depthFirstVisit = staticmethod(depthFirstVisit)

  def depthFirstSearch(graph, returnFinished = 0):
    '''This is a generator returning vertices in a depth-first traversal
       - If returnFinished is True, return a vertex when it finishes
       - Otherwise, return a vertex when it is first seen'''
    seen = []
    for vertex_index in graph.vertices.keys():
      vertex = graph.vertices[vertex_index]
      if not vertex in seen:
        try:
          for v in XAIFGraph.depthFirstVisit(graph, vertex, seen, returnFinished):
            yield v
        except StopIteration:
          pass
    return
  depthFirstSearch = staticmethod(depthFirstSearch)

  def breadthFirstSearch(graph, returnFinished = 0):
    '''This is a generator returning vertices in a breadth-first traversal
       - If returnFinished is True, return a vertex when it finishes
       - Otherwise, return a vertex when it is first seen'''
    #queue = XAIFGraph.getRoots(graph)[0:1]
    queue = XAIFGraph.getRoots(graph)
    if not len(queue): return
    seen  = [queue[0]]
    if not returnFinished:
      queue[0].__level = 0
      yield queue[0]
    while len(queue):
      vertex = queue[0]
      for v in graph.getEdges(vertex)[1].keys():
        if not v in seen:
          seen.append(v)
          v.incrementLevel()
          queue.append(v)
          if not returnFinished:
            yield v
      vertex = queue.pop(0)
      if returnFinished:
        yield vertex
    return
  breadthFirstSearch = staticmethod(breadthFirstSearch)

  def topologicalSort(graph):
    '''Reorder the vertices using topological sort'''
    vertices = [vertex for vertex in XAIFGraph.depthFirstSearch(graph, returnFinished = 1)]
    vertices.reverse()
    for vertex in vertices:
      yield vertex
    return
  topologicalSort = staticmethod(topologicalSort)



''' =================== Call graph ==================== '''

class XAIFCallGraph(XAIFGraph):
  def __init__(self):
    XAIFGraph.__init__(self)
    self.type = 'CallGraph'
    self.program_name = ''
    self.toplevel_routine_name = ''
    self.controlFlowGraphs = []
    self.scopeGraph = XAIFScopeHierarchy()
    self.indepVars = []
    self.depVars = []
    return

  def getProgramName(self):
    return self.program_name
  def setProgramName(self, prog):
    self.program_name = prog
    return

  def getTopLevelRoutineName(self):
    return self.toplevel_routine_name
  def setTopLevelRoutineName(self, top):
    self.toplevel_routine_name = top
    return
  
''' =================== Scoping and symbol tables ===================== '''

class XAIFScopeHierarchy(XAIFGraph):
  def __init__(self):
    XAIFGraph.__init__(self)
    self.type = 'ScopeHierarchy'
    return

class XAIFScope(XAIFVertex):
  def __init__(self, id):
    XAIFVertex.__init__(self, id)
    self.type = 'Scope'
    self.symbolTable = None
    return

  def getSymbolTable(self):
    return self.symbolTable

  def setSymbolTable(self, st):
    self.symbolTable = st
    return

class XAIFSymbolTable(XAIFVertex):
  def __init__(self, id):
    XAIFVertex.__init__(self, id)
    self.type = 'XAIFSymbolTable'
    self.symbols = {}
    self.scope_id = id
    return

  def getScopeId(self):
    return self.scope_id
  def setScopeId(self, scope_id):
    self.scope_id = scope_id
    return
  
class XAIFSymbol(object):
  def __init__(self, id, kind='variable', type='real', shape='scalar', frontend_tag=''):
    self.id = id
    self.type = 'Symbol'
    self.attr = {'symbol_id':id, 'kind':kind, 'type':type, 'shape':shape, 'frontend_tag':frontend_tag}
    return

  def getAttr(self, name=''):
    if name == '':
      return self.attr
    return self.attr(name)

  def setAttr(self, name, val):
    self.attr[name] = val
    return

''' =================== Control flow graph  ==================== '''

class XAIFControlFlowGraph(XAIFVertex,XAIFGraph):
  def __init__(self, id):
    XAIFGraph.__init__(self)
    XAIFVertex.__init__(self, id)
    self.type = 'ControlFlowGraph'    
    self.subroutine_name = ''
    self.argument_list = []  # List of XAIFArgumentSymbolReference instances
    return
  
  def getArgumentList(self):
    return self.argument_list
  def setArgumentList(self, args):
    self.argument_list = args
    return
  

class XAIFArgumentSymbolReference(object):
  def __init__(self):
    self.type = 'ArgumentSymbolReference'
    self.symbol_id = ''
    self.scope_id = ''
    return
 
  def getSymbolId(self):
    return symbol_id
  def setSymbolId(self, id):
    self.symbol_id = id
    return
 
  def getScopeId(self):
    return self.scope_id
  def setScopeId(self, id):
    self.scope_id = id
    return


''' ================ Basic block elements =============== '''

class XAIFBasicBlock(XAIFVertex):
  def __init__(self, id):
    XAIFVertex.__init__(self, id)
    self.type = 'BasicBlock'
    return

class XAIFBasicBlockElement(XAIFVertex):
  def __init__(self, id):
    XAIFVertex.__init__(self, id)
    self.type = 'BasicBlockElement'
    return
  
class XAIFAssignment(XAIFBasicBlockElement): 
  def __init__(self, id):
    XAIFBasicBlockElement.__init__(self, id)
    self.type = 'Assignment'
    self.lhs = None          # A Symbol reference
    self.rhs = XAIFGraph()   # An expression graph
    return

  def setLHS(self, lhs):
    self.lhs = lhs
    return

  def getRHS(self):
    return self.rhs

  def setRHS(self, rhs):
    self.rhs = rhs
    return
 

class XAIFSymbolReference(XAIFVertex):
  def __init__(self, id):
    XAIFVertex.__init__(self, id)
    self.type = 'SymbolReference'
    return

class XAIFVariableReference(XAIFVertex):
  def __init__(self, id):
    XAIFVertex.__init__(self, id)
    self.type = 'VariableReference'
    return
