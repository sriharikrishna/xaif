from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from xaifGraph import *
from XSV.driver import runit, runitAndShow
import sys
import re

''' Global entities: attributes, position in parse structure, etc. '''
position = 'None'
previous = 'None'

class XAIFParser(object):
  def __init__(self):
    self.callGraph = XAIFCallGraph()
    self.parser = make_parser()
    self.handler = XAIFContentHandler(self)
    self.parser.setContentHandler(self.handler)
    pass

  def parse(self, xmlfile):
    self.parser.parse(open(xmlfile))
    pass

  def validate(self, xmlfile, schema_list=[]):
    runitAndShow(xmlfile, schema_list)
    pass

  def displayGraph(self):
    print '======== Call Graph =========='
    self.callGraph.displaySorted()
    print '~~~~~~ Scope Hierarchy ~~~~~~~'
    self.callGraph.scopeGraph.displaySorted()
    pass


class XAIFContentHandler(ContentHandler):
  def __init__(self, parser):
    self.parser = parser
    self.current = 'None'
    self.context = 'None'
    self.currentScopeId = -1
    self.cfg = None
    self.parentVertex = None
    self.vertexList = []    # current (sub)graph vertices
    self.edgeList = []      # current (sub)graph edges
    ''' Set features for handler '''
    self.feature_validation = 1
    self.feature_external_ges = 1
    self.featuer_external_pes = 1
    pass

  def startElement(self, name, attrs):
    self.nonsname = re.match(r'xaif:(\w+)', name).group(1)
    self.current = self.nonsname
    v = None

    if self.nonsname == 'CallGraph':
      g = self.parseElement(attrs)

    ''' Scope hierarchy and symbol tables '''
    if self.nonsname == 'ScopeHierarchy':
      g = self.parseElement(attrs)
      self.parser.callGraph.scopeGraph = g
      self.edgeList = []

    if self.nonsname == 'Scope':
      v = self.parseElement(attrs) 
      self.parser.callGraph.scopeGraph.addVertex(v)
      self.currentScopeId = attrs.get('vertex_id','-1')
      self.parentVertex = v

    if self.nonsname == 'ScopeEdge':
      self.edgeList.append(self.parseEdge(attrs))

    if self.nonsname == 'SymbolTable':
      #v = self.parseElement(attrs, self.currentScopeId)
      v = self.parseElement(attrs)
      v.setScopeId(self.currentScopeId)
      self.parentVertex.setSymbolTable(v)

    if self.nonsname == 'Symbol':
      v = self.parseElement(attrs)
      
    ''' Control flow graph '''
    if self.nonsname == 'ControlFlowGraph':
      self.cfg = self.parseElement(attrs)
      self.parser.callGraph.addVertex(self.cfg)
      self.parentVertex = self.cfg

    if self.nonsname == 'ArgumentSymbolReference':
      v = self.parseElement(attrs)
      self.parentVertex.getArgumentList().append(v)

    if self.nonsname == 'Assignment':
      v = self.parseElement(attrs)
      self.parentVertex = v
 
    if self.nonsname == 'AssignmentLHS' or self.nonsname == 'AssignmentRHS':
      v = self.parentVertex
      
    if self.nonsname == 'VariableReference':
      v = self.parseElement(attrs)
      if self.context == 'AssignmentRHS':
        self.parentVertex.getRHS().addVertex(v)

    if self.nonsname == 'SymbolReference':
      v = self.parseElement(attrs)
      if self.context == 'AssignmentLHS':
        self.parentVertex.setLHS(v)

    if self.nonsname == 'ForLoop':
      v = self.parseElement(attrs)
      self.cfg.addVertex(v)
      self.parentVertex = v

    if self.nonsname == 'Initialization' and self.parentVertex.type == 'ForLoop':
      v = self.parseElement(attrs)
      self.parentVertex.setInit(v)
      self.parentVertex = v

    if self.nonsname == 'Update' and self.parentVertex.type == 'ForLoop':
      v = self.parseElement(attrs)
      self.parentVertex.setUpdate(v)
      self.parentVertex = v


    self.context = self.current
    return 

  def endElement(self, name):
    self.nonsname = re.match(r'xaif:(\w+)', name).group(1)
    self.current = self.nonsname
    v = None

    ''' Scope hierarchy and symbol tables '''
    if self.nonsname == 'ScopeHierarchy':
      for edge in self.edgeList:
        self.parser.callGraph.scopeGraph.addEdge(edge)
      self.edgeList = []

    pass

  def parseElement(self, attrs):
    '''
    Parse an element that is not a vertex, graph, or edge, instantiate
    proper XAIF object and set its attributes.
    '''
    el = eval('XAIF' + self.nonsname + '(attributes=attrs)')
    #el.setAttributes(attrs)
    return el 

  def parseEdge(self, attrs):
    ''' 
    Return an XAIFEdge corresponding to the edge element
    '''
    e = XAIFEdge(attrs.get('edge_id','-1'), attrs.get('source',''), attrs.get('target',''), attrs)
    print 'Parsed edge', e
    return e
  
  def parseExpressionEdge(self, attrs):
    '''
    Return an XAIFExpressionEdge corresponding to the ExpressionEdge element
    '''
    e = XAIFExpressionEdge(attrs.get('edge_id','-1'), attrs.get('source',''), attrs.get('target',''), attrs)
    return e
