#!/usr/bin/env python
from xaifGraph import XAIFGraph, XAIFVertex
from xaifParser import XAIFParser, XAIFContentHandler

# Test XAIF parsing, graph utilities

parser = XAIFParser()
#parser.validate("../schema/examples/uwe_ex_3.xaif")
parser.parse("../schema/examples/uwe_ex_3.xaif")
parser.displayGraph()
  
