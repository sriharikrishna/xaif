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
    self.graph = XAIFGraph()
    self.parser = make_parser()
    self.handler = XAIFContentHandler(self)
    self.parser.setContentHandler(self.handler)
    self.attributes = {'CallGraph':['program_name', 'toplevel_routine_name'],
		       'ScopeHierarchy':[],
		       'Scope':['vertex_id'],
		       'SymbolTable':[],
		       'ArgumentReference':['argument'],
		       'ControlFlowGraph':['vertex_id', 'subroutine_name'],
		       'ArgumentSymbolReference':['position', 'symbol_id', 'scope_id'],
		       'Entry':['vertex_id'],
		       'BasicBlock':['vertex_id'],
		       'Assignment':['statement_id'],
		       'VariableReference':['vertex_id'],
		       'SymbolReference':['vertex_id', 'symbol_id', 'scope_id'],
		       'Constant':['vertex_id', 'type', 'value']
		       }

    return

  def parse(self, xmlfile):
    self.parser.parse(open(xmlfile))
    return

  def validate(self, xmlfile, schema_list=["xaif.xsd"]):
    runitAndShow(xmlfile, schema_list)
    return

  def displayGraph(self):
    self.graph.display()
    return


class XAIFContentHandler(ContentHandler):
  def __init__(self, parser):
    self.parser = parser
    self.current = 'None'
    self.context = 'None'
    self.currentScopeId = -1
    self.parentVertex = None
    ''' Set features for handler '''
    self.feature_validation = 1
    self.feature_external_ges = 1
    self.featuer_external_pes = 1
    return

  def startElement(self, name, attrs):
    self.nonsname = re.match(r'xaif:(\w+)', name).group(1)
    self.current = self.nonsname
    v = None

    if self.nonsname == 'CallGraph':
      v = self.parseElement(attrs)

    ''' Scope hierarchy and symbol tables '''
    if self.nonsname == 'ScopeHierarchy':
      v = self.parseElement(attrs)

    if self.nonsname == 'Scope':
      v = self.parseElement(attrs, attrs.get('vertex_id','-1'))
      self.currentScopeId = attrs.get('vertex_id','-1')

    if self.nonsname == 'SymbolTable':
      v = self.parseElement(attrs, self.currentScopeId)

    ''' Control flow graph '''
    if self.nonsname == 'ControlFlowGraph':
      v = self.parseElement(attrs,attrs.get('vertex_id'))

    if self.nonsname == 'Assignment':
      v = self.parseElement(attrs,attrs.get('statement_id'))
      self.parentVertex = v
 
    if self.nonsname == 'AssignmentLHS' or self.nonsname == 'AssignmentRHS':
      v = self.parentVertex
      
    if self.nonsname == 'VariableReference':
      v = self.parseElement(attrs,attrs.get('vertex_id'))
      if self.context == 'AssignmentRHS':
        self.parentVertex.getRHS().addVertex(v)

    if self.nonsname == 'SymbolReference':
      v = self.parseElement(attrs,attrs.get('vertex_id'))
      if self.context == 'AssignmentLHS':
        self.parentVertex.setLHS(v)
        

    self.context = self.current
    return 



    return

  def endElement(self, name):
    return

  def parseElement(self, attrs, id='-1'):
    ''' 
    Return an XAIFVertex corresponding to the element with (no-namespace) name
    self.nonsname, setting all attributes accordingly
    '''
    print 'Parsing ' + self.nonsname
    v = eval('XAIF' + self.nonsname + '(\'' + id + '\')')
    v.setAttributes(self.parser.attributes[self.nonsname], attrs)
    self.parser.graph.addVertex(v)
    return v




  
