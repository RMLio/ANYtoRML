import sys,getopt,logging
import rdflib, re, time, datetime

from rdflib import Graph, Namespace, URIRef, BNode, RDF, Literal, plugin
from rdflib.namespace import RDF, XSD

RML    = Namespace("http://semweb.mmlab.be/ns/rml#")
R2RML  = Namespace("http://www.w3.org/ns/r2rml#")

logging.basicConfig(filename='RMLgenerator.log',level=logging.DEBUG)

newg=rdflib.Graph()

newg.bind("rr",      URIRef("http://www.w3.org/ns/r2rml#"))
newg.bind("rml",     URIRef("http://semweb.mmlab.be/ns/rml#"))
newg.bind("dc",      URIRef("http://purl.org/dc/elements/1.1/"))
newg.bind("dcterms", URIRef("http://purl.org/dc/terms/"))
newg.bind("xsd",     URIRef("http://www.w3.org/2001/XMLSchema#"))
newg.bind("owl",     URIRef("http://www.w3.org/2002/07/owl#"))
newg.bind("rdf",     URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#"))
newg.bind("rdfs",    URIRef("http://www.w3.org/2000/01/rdf-schema#"))
newg.bind("foaf",    URIRef("http://xmlns.com/foaf/0.1/"))


# Triples Map Generation

def TriplesMapGeneration(resource,logicalSource):
   newg.add([resource, RDF.type, R2RML.TriplesMap])
   newg.add([resource, RML.logicalSource, logicalSource])


# Logical Table Generation

def LogicalTableGeneration(subject):
   global logicalTableNode
   logicalTableNode = subject + "_LogicalTable"
   newg.add([subject, URIRef('http://www.w3.org/ns/r2rml#logicalTable'),URIRef(logicalTableNode)])
   newg.add([URIRef(logicalTableNode), RDF.type, URIRef('http://www.w3.org/ns/r2rml#LogicalTable')])


# Logical Source Generation

def LogicalSourceGeneration(logicalSource,source):
   global logicalSourceNode
   logicalSourceNode = logicalSource
   if(source):
      newg.add([logicalSourceNode, RML.source,source])
   newg.add([logicalSourceNode, RDF.type, RML.LogicalSource])


# Subject Map Generation

def SubjectMapGeneration(tm,subject):
   newg.add([tm, R2RML.subjectMap,subject])
   newg.add([subject, RDF.type, R2RML.SubjectMap])


# Logical Source Class Generation

def ClassGeneration(subject,classValue):
   newg.add([subject, URIRef(R2RML + 'class'), classValue])


# Subject Map Template Generation

def SubjectMapTemplateGeneration(resource,pattern):
   global subjectNode

   if(pattern != "null"):
      newg.add([subjectNode, R2RML.template,Literal(pattern)])


# Predicate Object Map Generation

def PredicateObjectMapGeneration(tmResource,preObj):
   newg.add([tmResource, R2RML.predicateObjectMap, preObj])
   newg.add([preObj, RDF.type, R2RML.PredicateObjectMap])


# Predicate Map Generation

def PredicateMapGeneration(pValue,preObj):
   uriResource = BNode()
   newg.add([preObj, R2RML.predicateMap, uriResource])
   newg.add([uriResource, RDF.type, R2RML.PredicateMap])
   newg.add([uriResource, R2RML.constant, URIRef(pValue)])


# Object Map Generation

def ObjectMapGeneration(oValue,preObj,termType):
   uriResource = BNode().skolemize()
   newg.add([preObj, R2RML.objectMap, uriResource])
   newg.add([uriResource, RDF.type, R2RML.ObjectMap])
   if(termType == 'reference-valued'):
      newg.add([uriResource, RML.reference, oValue])
   elif(termType == 'template-valued'):
      newg.add([uriResource, R2RML.template, oValue])
   elif(termType == 'constant'):
      newg.add([uriResource, R2RML.constant, oValue])

   return uriResource


# Datatype Generation

def DatatypeGeneration(datatype,objMap):
   print 'objMap ' + objMap
   newg.add([objMap, R2RML.datatype, XSD[datatype]])
   #TODO: Add exceptions


# Referencing Object Map Generation

def RefObjectMapGeneration(preObj,objNode,tmResource):
   global newg
   global subjectNode
   newg.add([preObj, R2RML.objectMap, objNode])
   newg.add([objNode, RDF.type, R2RML.RefObjectMap])
   newg.add([objNode, R2RML.parentTriplesMap, tmResource])


# Join Condition Generation

def JoinConditionGeneration(objNode):
   pass
   numJoins = 0
   for preObj,pre,obj in g.triples( (preObj,  URIRef('http://www.wiwiss.fu-berlin.de/suhl/bizer/D2RQ/0.1#join'), None) ):
      joinNode = objNode + "_JoinMap_" + str(numJoins)
      numJoins = numJoins + 1
      newg.add([objNode, URIRef('http://www.w3.org/ns/r2rml#joinCondition'), URIRef(joinNode)])
      table = re.split(' |=',obj)
      newg.add([joinNode, RDF.type, URIRef('http://www.w3.org/ns/r2rml#Join')])
      
      for subject,pred,obj in newg.triples( (subjectNode, URIRef('http://www.w3.org/ns/r2rml#logicalTable'), None) ):
         for obj,predd,tab in newg.triples( (obj, URIRef('http://www.w3.org/ns/r2rml#tableName'), None) ):
            pp = re.compile( '.')
            mm = re.search('(.+?)\.', table[0])
            if str(mm.group(1)) == str(tab):
               reference = table[len(table)-1].replace(re.search('(.+?)\.', table[len(table)-1]).group(1)+".","")
               newg.add([URIRef(joinNode), URIRef('http://www.w3.org/ns/r2rml#parent'), Literal(reference)])
               reference = table[0].replace(re.search('(.+?)\.', table[0]).group(1)+".","")
               newg.add([URIRef(joinNode), URIRef('http://www.w3.org/ns/r2rml#child'), Literal(reference)])
            else:
               reference = table[0].replace(re.search('(.+?)\.', table[0]).group(1)+".","")
               newg.add([URIRef(joinNode), URIRef('http://www.w3.org/ns/r2rml#parent'), Literal(reference)])
               reference = table[len(table)-1].replace(re.search('(.+?)\.', table[len(table)-1]).group(1)+".","")
               newg.add([URIRef(joinNode), URIRef('http://www.w3.org/ns/r2rml#child'), Literal(table[len(table)-1])])


# Results Generation

def resultsGeneration(outputfile):
   print("RML graph has %s statements." % len(newg))
   now = datetime.datetime.now()
   newg.add( (BNode(), URIRef("http://purl.org/dc/elements/1.1/created"), 
      Literal(time.strftime(str(now.year)+"-"+str(now.month)+"-"+str(now.day))) ) ) 
   newg.serialize(outputfile,format='turtle')