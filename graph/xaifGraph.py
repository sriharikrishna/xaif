##from __future__ import generators
import types

class XAIFObject:
  def __init__(self, attributes=None, type='XAIFObject'):
    self.type = type
    self.attrs = {}
    self.unique_id_key = ''
    if not attributes is None: self.setAttributes(attributes)
    pass

  def getAttributes(self):
    return self.attr
  
  def setAttributes(self, attrs):
    ''' names: string list
    attrs: xml.sax attribute structure, must have get(name) method'''
    for attr_name in self.attrs.keys():
      self.attr[attr_name] = attrs.get(attr_name)
    pass

  def getAttribute(self, key):
    if key in self.attr: 
      return self.attr[key]
    else:
      return None

  def setAttribute(self, key, value):
    self.attr[key] = value
    pass  

  def getType(self):
    return self.type
  def setType(self, type):
    self.type = type
    pass

class XAIFVertex (XAIFObject):
  def __init__(self, attributes=None, type='XAIFVertex'):
    self.attr = {'vertex_id':''}
    XAIFObject.__init__(self, attributes, type)
    self.unique_id_key = 'vertex_id'
    self.id = id
    self.__level = 0
    pass
 
  def __str__(self):
    return 'vertex <%s:%s:%s>' % (self.type, self.id, self.attr)

  def getId(self):
    return self.id
  def setId(self, id):
    self.id = id
    self.attr['vertex_id'] = id
    pass

  def getLevel(self):
    return self.__level
  def setLevel(self, lev=0):
    self.__level = lev
    pass
  def incrementLevel(self):
    self.__level = self.__level + 1
    return self.__level

class XAIFEdge(XAIFObject):
  def __init__(self, id, src, tgt, attributes):
    self.attr = {'edge_id':id, 'source':src, 'target':tgt, 'position':'1'}
    XAIFObject.__init__(self, attributes, 'XAIFEdge')
    self.type = 'Edge'
    self.source = src
    self.target = tgt
    self.unique_id_key = 'edge_id'
    self.id = id
    pass

  def __str__(self):
    return 'id: %s, source: %s, target: %s' % (self.attr['edge_id'], self.attr['source'], self.attr['target'])

  def getSource(self):
    return self.source
    
  def setSource(self, srcvertex):
    self.attr['source'] = srcvertex
    self.source = srcvertex
    pass

  def getTarget(self):
    return self.target
    
  def setTarget(self, tgtvertex):
    self.attr['target'] = tgtvertex
    self.target = tgtvertex
    pass

class XAIFGraph(XAIFObject):
  def __init__(self, vertices = {}, attributes=None):
    self.attrs = {}
    XAIFObject.__init__(self, attributes, 'XAIFGraph')
    '''Create a graph'''
    self.vertices = {}
    '''Edges are dictionaries with start vertex keys, and values that are dictionaries
       whose keys are the target vertex keys and values are pointer to vertices.
       For example, edge[v1][v2] is the data (or label) of the edge from v1 to v2'''
    self.inEdges  = {}
    self.outEdges = {}
    self.roots = []
    self.leaves = []
    ##map(self.addVertex, vertices)
    for index in vertices.keys():
      self.addVertex(vertices[index])
    pass

  def __str__(self):
    return 'XAIFGraph with '+str(len(self.vertices))+' vertices and '+str(reduce(lambda k,l: k+l, [len(edgeList) for edgeList in self.inEdges.values()], 0))+' edges'

  def addVertex(self, vertex):
    '''Add a vertex if it does not already exist in the vertex list
       - Should be able to use Set in Python 2.3'''
    if vertex is None: return
    if not vertex.getId() in self.vertices.keys():
      self.vertices[vertex.getId()] = vertex
      self.clearEdges(vertex)
    pass

  def addVertexWithId(self, vertex_id):
    '''Add a vertex if it does not already exist in the vertex list
       - Should be able to use Set in Python 2.3'''
    if vertex_id is None: return
    if not vertex_id in self.vertices.keys():
      self.vertices[vertex_id] = XAIFVertex()
      self.vertices[vertex_id].setId(vertex_id)
      self.clearEdges(self.vertices[vertex_id])
    pass
  def addEdge(self, edge):
    '''Add an XAIFEdge to the graph'''
    self.addVertexWithId(edge.getSource())
    self.addVertexWithId(edge.getTarget())
    src = self.vertices[edge.getSource()]
    tgt = self.vertices[edge.getTarget()]
    if not src in self.inEdges[tgt].keys(): self.inEdges[tgt][src] = None
    if not tgt in self.outEdges[src].keys(): self.outEdges[src][tgt] = None
    pass
  
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
    pass

  def getEdges(self, vertex):
    '''vertex is of type XAIFVertex'''
    return (self.inEdges[vertex], self.outEdges[vertex])

  def clearEdges(self, vertex):
    self.inEdges[vertex]  = {}
    self.outEdges[vertex] = {}
    pass

  def annotateEdge(self, srcVertex, tgtVertex, data = None):
    self.addVertex(srcVertex)
    self.addVertex(tgtVertex)
    self.addEdges(srcVertex,[],[tgtVertex])
    self.outEdges[srcVertex][tgtVertex] = data
    self.inEdges[tgtVertex][srcVertex] = data
    pass

  def clearEdgeAnnotations(self, srcVertex, tgtVertex):
    self.outEdges[srcVertex][tgtVertex] = None
    self.inEdges[tgtVertex][srcVertex] = None
    pass

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
    pass

  def addSubgraph(self, graph):
    '''Add the vertices and edges of another graph into this one'''
    ##map(self.addVertex, graph.vertices)
    for index in graph.vertices.keys():
      self.addVertex(vertices[index])

    ##map(lambda v: apply(self.addEdges, (v,)+graph.getEdges(v)), graph.vertices)
    for index in graph.vertices.keys():
      f = lambda v: apply(self.addEdges, (v,)+graph.getEdges(v))
      f(graph.vertices[index])
    pass

  def removeSubgraph(self, graph):
    '''Remove the vertices and edges of a subgraph, and all the edges connected to it'''
    ##map(self.removeVertex, graph.vertices)
    for index in graph.vertices.keys():
      self.removeVertex(vertices[index])
    pass

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
    pass

  def displaySorted(self, init_level=0):
    #print 'I am an XAIFGraph with '+str(len(self.vertices))+' vertices'
    #print 'BreadthFirstSearch:'
    dvisitor = displayBFVisitor()
    for root_vertex in XAIFGraph.getRoots(self):
      #for vertex in XAIFGraph.breadthFirstSearch(self,1,init_level):
      XAIFGraph.BFSearch(self, root_vertex, init_level, visitor=dvisitor)
      
##      for vertex in XAIFGraph.BFSearch(self, root_vertex, init_level, visitor=dvisitor):
##        self.printIndent(vertex.getLevel() + init_level)
##        inedges, outedges = [], []
##        for v in self.inEdges[vertex]: inedges.append(str(v))
##        for v in self.outEdges[vertex]: outedges.append(str(v))
##        print vertex, ' in: ', inedges, ' out: ', outedges
##        if vertex.type == 'ControlFlowGraph': vertex.displaySorted(vertex.getLevel()+1)
        
##    print '\nDepthFirstSearch:'
##    for vertex in XAIFGraph.depthFirstSearch(self, 1):
##      self.printIndent(vertex.getLevel())
##      inedges, outedges = [], []
##      for v in self.inEdges[vertex]: inedges.append(str(v))
##      for v in self.outEdges[vertex]: outedges.append(str(v))
##      print vertex, ' in: ', inedges, ' out: ', outedges
      #print '('+str(self.vertices.index(vertex))+') '+str(vertex)+' in: '+str(map(self.vertices.index, self.inEdges[vertex]))+' out: '+str(map(self.vertices.index, self.outEdges[vertex]))
    pass

##  def appendGraph(self, graph):
##    '''Join every leaf of this graph to every root of the input graph, leaving the result in this graph'''
##    leaves = XAIFGraph.getLeaves(self)
##    self.addSubgraph(graph)
##    map(lambda v: self.addEdges(v, outputs = XAIFGraph.getRoots(graph)), leaves)
##    return self

##  def prependGraph(self, graph):
##    '''Join every leaf of the input graph to every root of this graph, leaving the result in this graph'''
##    roots = XAIFGraph.getRoots(self)
##    self.addSubgraph(graph)
##    map(lambda v: self.addEdges(v, outputs = roots), XAIFGraph.getLeaves(graph))
##    return self

  def getRoots(graph):
    '''Return all the sources in the graph (nodes without entering edges)'''
    graph.roots = []
    for i in graph.vertices.keys():
      v = graph.vertices[i]
      if not len(graph.getEdges(v)[0]):
        graph.roots.append(v)
    return graph.roots
    #return filter(lambda v: not len(graph.getEdges(v)[0]), graph.vertices)
  ##getRoots = staticmethod(getRoots)

  def getLeaves(graph):
    '''Return all the sinks in the graph (nodes without exiting edges)'''
    graph.leaves = []
    for i in graph.vertices.keys():
      v = graph.vertices[i]
      if not len(graph.getEdges(v)[1]):
        graph.leaves.append(v)
    return graph.leaves
    #return filter(lambda v: not len(graph.getEdges(v)[1]), graph.vertices)
  ##getLeaves = staticmethod(getLeaves)

##  def depthFirstVisit(graph, vertex, seen = None, returnFinished = 0):
##    '''This is a generator returning vertices in a depth-first traversal only for the subtree rooted at vertex'''
##    if seen is None: seen = []
##    seen.append(vertex)
##    if not returnFinished:
##      yield vertex
##    for v in graph.getEdges(vertex)[1]:
##       if not v in seen:
##        try:
##          for v2 in XAIFGraph.depthFirstVisit(graph, v, seen, returnFinished):
##            yield v2
##        except StopIteration:
##          pass
##    if returnFinished:
##      yield vertex
##    return
##  depthFirstVisit = staticmethod(depthFirstVisit)

##  def depthFirstSearch(graph, returnFinished = 0):
##    '''This is a generator returning vertices in a depth-first traversal
##       - If returnFinished is True, return a vertex when it finishes
##       - Otherwise, return a vertex when it is first seen'''
##    seen = []
##    for vertex_index in graph.vertices.keys():
##      vertex = graph.vertices[vertex_index]
##      if not vertex in seen:
##        try:
##          for v in XAIFGraph.depthFirstVisit(graph, vertex, seen, returnFinished):
##            yield v
##        except StopIteration:
##          pass
##    return
##  depthFirstSearch = staticmethod(depthFirstSearch)

##  def breadthFirstSearch(graph, returnFinished = 0, init_level = 0):
##    '''This is a generator returning vertices in a breadth-first traversal
##       - If returnFinished is True, return a vertex when it finishes
##       - Otherwise, return a vertex when it is first seen'''
##    #queue = XAIFGraph.getRoots(graph)[0:1]
##    queue = XAIFGraph.getRoots(graph)
##    if not len(queue): return
##    seen  = [queue[0]]
##    if not returnFinished:
##      queue[0].__level = init_level
##      yield queue[0]
##    while len(queue):
##      vertex = queue[0]
##      for v in graph.getEdges(vertex)[1].keys():
##        if not v in seen:
##          seen.append(v)
##          v.incrementLevel()
##          queue.append(v)
##          if not returnFinished:
##            yield v
##      vertex = queue.pop(0)
##      if returnFinished:
##        yield vertex
##    return
##  breadthFirstSearch = staticmethod(breadthFirstSearch)
    
##  def topologicalSort(graph):
##    '''Reorder the vertices using topological sort'''
##    vertices = [vertex for vertex in XAIFGraph.depthFirstSearch(graph, returnFinished = 1)]
##    vertices.reverse()
##    for vertex in vertices:
##      yield vertex
##    return
##  topologicalSort = staticmethod(topologicalSort)


  def BFSearch(graph, start_vertex, init_level=0, visitor=None):
    queue = []
    seen = []
    color = {}
    for vertex_index in graph.vertices.keys():
      vertex = graph.vertices[vertex_index]
      color[vertex] = 1          # WHITE
      if not visitor is None: visitor.visitInitVertex(vertex, graph)
      
    color[start_vertex] = 2      # GRAY
    seen.append(start_vertex)
    start_vertex.__level = init_level
    queue.append(start_vertex)
    if not visitor is None: visitor.visitDiscoverVertex(vertex, graph)
    
    while len(queue):
      u = queue.pop(0)
      if not visitor is None: visitor.visitExamineVertex(u, graph)

      # Need to add edge visitor calls
      outedges = graph.getEdges(u)[1];
      
      for v in outedges.keys():
        if (color[v] == 1):      # WHITE        (u, v) is a tree edge
          ##if not visitor is None: visitor.visitTreeEdge(edge, graph)
          color[v] = 2           # GRAY
          seen.append(v)
          v.incrementLevel()
          queue.append(v)
          if not visitor is None: visitor.visitDiscoverVertex(v, graph)
          
        else:                    # (u, v) is a non-tree edge
          ##if not visitor is None: visitor.visitNontreeEdge(edge, graph)
          if (color[v] == 2):    # GRAY
            # edge (u, v) has a gray target
            ##if not visitor is None: visitor.visitGrayTarget(edge, graph)
            pass
          else:
            # edge (u, v) has a black target
            ##if not visitor is None: visitor.visitBlackTarget(edge, graph)
            pass
      color[u] = 3          # BLACK
      if not visitor is None: visitor.visitFinishVertex(u,graph)

    return seen
  
              
    
''' =========================================================== '''
'''                 Breadth First Search Visitor                '''
''' =========================================================== '''
class BFVisitor (XAIFObject):
  def __init__(self):
    pass

  def visitInitVertex(self, vertex, graph):
    pass

  def visitDiscoverVertex(self, vertex, graph):
    pass

  def visitExamineVertex(self, vertex, graph):
    pass

  def visitExamineEdge(self, edge, graph):
    pass

  def visitTreeEdge(self, edge, graph):
    pass

  def visitNontreeEdge(self, edge, graph):
    pass

  def visitGrayTarget(self, edge, graph):
    pass

  def visitBlackTarget(self, edge, graph):
    pass

  def visitFinishVertex(self, vertex, graph):
    pass


''' Simple BF Visitor '''
class displayBFVisitor(BFVisitor):
  def __init__(self):
    BFVisitor.__init__(self)
    self.init_level = 0
    pass
  
  def visitDiscoverVertex(self, vertex, graph):
    ##print 'Visitor: discovering vertex', vertex
    graph.printIndent(vertex.getLevel() + self.init_level)
    inedges, outedges = [], []
    for v in graph.inEdges[vertex]: inedges.append(str(v))
    for v in graph.outEdges[vertex]: outedges.append(str(v))
    print vertex, ' in: ', inedges, ' out: ', outedges
 
    pass

  
''' =========================================================== '''
'''                           Call graph                        '''
''' =========================================================== '''

class XAIFCallGraph(XAIFGraph):
  def __init__(self, vertices={}, attributes=None):
    self.attr = {'program_name':'', 'toplevel_routine_name':''}
    XAIFGraph.__init__(self, vertices, attributes)
    self.setType('CallGraph')
    self.unique_id_key = 'program_name'
    self.controlFlowGraphs = []
    self.scopeGraph = XAIFScopeHierarchy()
    self.indepVars = []
    self.depVars = []
    pass


  
''' =========================================================== '''
'''                     Scoping and symbols                     '''
''' =========================================================== '''

class XAIFScopeHierarchy(XAIFGraph):
  def __init__(self, vertices={}, attributes=None):
    self.attr = {}
    XAIFGraph.__init__(self, vertices, attributes)
    self.setType('ScopeHierarchy')
    pass

class XAIFScope(XAIFVertex):
  def __init__(self, attributes=None):
    self.attr = {'vertex_id':''}
    XAIFVertex.__init__(self, attributes, 'Scope')
    self.unique_id_key = 'vertex_id'
    self.symbolTable = None
    pass

  def getSymbolTable(self):
    return self.symbolTable

  def setSymbolTable(self, st):
    self.symbolTable = st
    pass

class XAIFSymbolTable(XAIFVertex):
  def __init__(self, attributes=None):
    self.attr = {}
    XAIFVertex.__init__(self, attributes, 'SymbolTable')
    self.unique_id_key = ''
    self.symbols = {}
    self.scope_id = -1
    pass

  def getScopeId(self):
    return self.scope_id
  def setScopeId(self, scope_id):
    self.scope_id = scope_id
    pass
  
class XAIFSymbol(XAIFObject):
  def __init__(self, attributes=None):
    self.attr = {'symbol_id':'', 'kind':'variable', 'type':'real', 'shape':'scalar', 'annotation':''}
    XAIFObject.__init__(self, attributes, 'Symbol')
    self.unique_id_key = 'symbol_id'
    pass


class XAIFSymbolReference(XAIFVertex):
  def __init__(self, attributes=None):
    self.attr = {'vertex_id':'', 'symbol_id':'', 'scope_id':''}
    XAIFVertex.__init__(self, attributes, 'SymbolReference')
    self.unique_id_key = 'vertex_id'
    pass

class XAIFVariableReference(XAIFVertex):
  def __init__(self, attributes=None):
    self.attr = {'vertex_id':''}
    XAIFVertex.__init__(self, attributes, 'VariableReference')
    self.unique_id_key = 'vertex_id'
    pass

''' =========================================================== '''
'''                     Control flow graph                      '''
''' =========================================================== '''

class XAIFControlFlowGraph(XAIFVertex,XAIFGraph):
  def __init__(self, vertices={}, attributes=None):
    self.attr = {'vertex_id':'', 'subroutine_name':''}    
    XAIFGraph.__init__(self, vertices, attributes)
    XAIFVertex.__init__(self, attributes, 'ControlFlowGraph')
    self.unique_id_key = 'vertex_id'
    self.argument_list = []  # List of XAIFArgumentSymbolReference instances
    pass
  
  def getArgumentList(self):
    return self.argument_list
  def setArgumentList(self, args):
    self.argument_list = args
    pass
  
class XAIFArgumentSymbolReference(XAIFObject):
  def __init__(self, attributes=None):
    self.attr = {'position':'1', 'symbol_id':'', 'scope_id':''}
    XAIFObject.__init__(self, attributes, 'ArgumentSymbolReference')
    self.unique_id_key = 'symbol_id'  # within a given scope
    pass

''' =========================================================== '''
'''                    Basic block elements                     '''
''' =========================================================== '''

class XAIFBasicBlock(XAIFVertex):
  def __init__(self, attributes=None):
    XAIFVertex.__init__(self, attributes, 'BasicBlock')
    pass

class XAIFBasicBlockElement(XAIFVertex):
  def __init__(self, attributes=None, type='BasicBlockElement'):
    XAIFVertex.__init__(self, attributes, type)
    pass
  
class XAIFAssignment(XAIFBasicBlockElement): 
  def __init__(self, attributes=None, type='Assignment'):
    self.attr = {'statement_id':''}
    XAIFBasicBlockElement.__init__(self, attributes, type)
    self.unique_id_key = 'statement_id'
    self.lhs = None                    # A Symbol reference
    self.rhs = XAIFExpressionGraph()   # An expression graph
    pass

  def setLHS(self, lhs):
    self.lhs = lhs
    pass

  def getRHS(self):
    return self.rhs

  def setRHS(self, rhs):
    self.rhs = rhs
    pass
 
class XAIFForLoop(XAIFVertex):
  def __init__(self, attributes=None):
    XAIFVertex.__init__(self, attributes, 'ForLoop')
    self.id = self.attr[self.unique_id_key]
    self.init = None
    self.cond = None
    self.update = None
    pass

  def setInit(self, init):
    self.init = init
    pass

  def setCondition(self, cond):
    self.cond = cond
    pass

  def setUpdate(self, update):
    self.update = update
    pass


class XAIFInitialization(XAIFAssignment):
  def __init__(self, attributes = None):
    self.attr = {'statement_id':id}
    XAIFAssignment.__init__(self, attributes, 'Initialization')
    self.unique_id_key = 'statement_id'
    self.lhs = None          # A Symbol reference
    self.rhs = XAIFExpressionGraph()   # An expression graph
    pass
 
class XAIFForLoopCondition(XAIFObject):
  def __init__(self, attributes=None):
    self.attr = {}
    XAIFObject.__init__(self, attributes, 'ForLoopCondition')
    self.lhs = None                    # A Symbol reference
    self.rhs = XAIFExpressionGraph()   # An expression graph
    pass

class XAIFUpdate(XAIFAssignment):
  def __init__(self, attributes = None):
    self.attr = {'statement_id':''}
    XAIFAssignment.__init__(self, attributes, 'Update')
    self.unique_id_key = 'statement_id'
    self.lhs = None          # A Symbol reference
    self.rhs = XAIFExpressionGraph()   # An expression graph
    pass
 
 
''' =========================================================== '''
'''                    Expression elements                      '''
''' =========================================================== '''

class XAIFExpressionGraph(XAIFGraph):
  def __init__(self, vertices={}, attributes = None):
    self.attr = {}
    XAIFGraph.__init__(self, vertices, attributes)
    self.setType('ExpressionGraph')
    pass

class XAIFExpressionEdge(XAIFEdge):
  def __init__(self, id, src, tgt, attributes = None):
    XAIFEdge.__init__(self, id, src, tgt, attributes)
    self.setType('ExpressionEdge')
    pass
