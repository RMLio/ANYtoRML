import RMLgenerator
import sys,getopt,logging
import rdflib, re, time, datetime

from rdflib import Graph, Namespace, URIRef, BNode, RDF, Literal, plugin
from rdflib.namespace import RDF, XSD
from rdflib.serializer import Serializer

logging.basicConfig(filename='R2RMLtoRML.log',level=logging.DEBUG)

RML    = Namespace("http://semweb.mmlab.be/ns/rml#")
R2RML  = Namespace("http://www.w3.org/ns/r2rml#")
D2RQ   = Namespace("http://www.wiwiss.fu-berlin.de/suhl/bizer/D2RQ/0.1#")

g=rdflib.Graph()
g.bind("rml",     URIRef("http://semweb.mmlab.be/ns/rml#"))
g.bind("d2rq",    URIRef("http://www.wiwiss.fu-berlin.de/suhl/bizer/D2RQ/0.1#"))

def databaseAccessibility(source):
	g.add((source,RDF.type,D2RQ.Database))
	g.add((source,D2RQ.jdbcDSN,Literal("jdbc:mysql://localhost/example")))
	g.add((source,D2RQ.jdbcDriver,Literal("com.mysql.jdbc.Driver")))
	g.add((source,D2RQ.username,Literal("username")))
	g.add((source,D2RQ.password,Literal("password")))

def R2RMLtoRML(inputfile):
	g.parse(inputfile, format='turtle')
	print("R2RML graph has %s statements." % len(g))

	for subject,predicate,object in g.triples( (None, URIRef(R2RML.logicalTable), None) ):
		g.remove((subject,predicate,object))
		g.add((subject,RML.logicalSource,object))
		g.add((object,RML.referenceFormulation,R2RML.SQL2008))
		source = BNode()
		databaseAccessibility(source)
		g.add((object,RML.source,source))

	for subject,predicate,object in g.triples( (None, URIRef(R2RML.column), None) ):
		g.remove((subject,predicate,object))
		g.add((subject,RML.reference,object))

def resultsGeneration(outputfile):
	print("RML graph has %s statements." % len(g))
	g.serialize(outputfile,format='turtle')