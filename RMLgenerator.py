import sys,getopt,logging
import rdflib, re, time, datetime

from rdflib import Graph, Namespace, URIRef, BNode, RDF, Literal, plugin
from rdflib.namespace import RDF, XSD

RML    = Namespace("http://semweb.mmlab.be/ns/rml#")
R2RML  = Namespace("http://www.w3.org/ns/r2rml#")

logging.basicConfig(filename='CSVWtoRML.log',level=logging.DEBUG)

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

def LogicalTableGeneration(subject):
   global logicalTableNode
   logicalTableNode = subject + "_LogicalTable"
   newg.add([subject, URIRef('http://www.w3.org/ns/r2rml#logicalTable'),URIRef(logicalTableNode)])
   newg.add([URIRef(logicalTableNode), RDF.type, URIRef('http://www.w3.org/ns/r2rml#LogicalTable')])

def LogicalSourceGeneration(resource):
   global logicalSourceNode
   logicalSourceNode = resource + '_LogicalSource'
   newg.add([URIRef(resource), URIRef(RML.logicalSource),URIRef(logicalSourceNode)])
   newg.add([URIRef(logicalSourceNode), RDF.type, URIRef(RML.LogicalSource)])

def TriplesMapGeneration(resource):
   newg.add([resource.skolemize(), RDF.type, URIRef(R2RML.TriplesMap)])

def SubjectMapGeneration(tm,subject):
   global newg
   #global subjectNode
   #subjectNode = BNode(resource + "_subjectMap")
   newg.add([tm, URIRef(R2RML.subjectMap),subject])
   newg.add([subject, RDF.type, URIRef(R2RML.SubjectMap)])

def ClassGeneration(subject,classValue):
   #global subjectNode
   newg.add([subject, URIRef(R2RML + 'class'), URIRef(classValue)])

def SubjectMapTemplateGeneration(resource,pattern):
   global tableName
   global subjectNode

   if(pattern != "null"):
      newg.add([subjectNode, URIRef(R2RML.template),Literal(pattern)])
   #else: 
   #   for resource,predicate,object in g.triples( 
   #      (resource,  URIRef(u'http://www.wiwiss.fu-berlin.de/suhl/bizer/D2RQ/0.1#uriPattern'), None) ):
   #      tableName = re.search('(.+?)\.', re.search('@@(.+?)@@', object).group(1)).group(1)
   #      newg.add([URIRef(logicalTableNode), URIRef('http://www.w3.org/ns/r2rml#tableName'),Literal(tableName)])
   #      p = re.compile( '@@(.+?)@@')
         #R2RML doesn't support urlencode and urlify, thus skipped
   #      new_obj = p.sub( r'{\1}', object.replace("|urlencode","").replace("|urlify",""))
   #      reference = new_obj.replace(re.search('{(.+?)\.', new_obj).group(1)+".","")
   #      newg.add([subjectNode, URIRef('rr:template'),Literal(reference)])
   #   if((resource,URIRef('http://www.wiwiss.fu-berlin.de/suhl/bizer/D2RQ/0.1#class'),None) in g):
   #      for resource,predicate,object in g.triples( (resource,  URIRef(u'http://www.wiwiss.fu-berlin.de/suhl/bizer/D2RQ/0.1#class'), None) ):
   #         newg.add([subjectNode, URIRef('rr:class'),URIRef(object)])

def PredicateObjectMapGeneration(tmResource,preObj):
   newg.add([tmResource.skolemize(), URIRef(R2RML.predicateObjectMap), preObj.skolemize()])
   newg.add([preObj.skolemize(), RDF.type, URIRef(R2RML.PredicateObjectMap)])

def PredicateMapGeneration(pValue,preObj):
   uriResource = BNode()
   newg.add([preObj.skolemize(), URIRef(R2RML.predicateMap), uriResource.skolemize()])
   newg.add([uriResource.skolemize(), RDF.type, URIRef(R2RML.PredicateMap)])
   newg.add([uriResource.skolemize(), URIRef(R2RML.constant), URIRef(pValue)])

def ObjectMapGeneration(oValue,preObj):
   uriResource = BNode()
   newg.add([preObj.skolemize(), URIRef(R2RML.objectMap), uriResource.skolemize()])
   newg.add([uriResource.skolemize(), RDF.type, URIRef(R2RML.ObjectMap)])
   newg.add([uriResource.skolemize(), URIRef(RML.reference), oValue])
   return uriResource

def DatatypeGeneration(datatype,objMap):
   print 'objMap ' + objMap
   newg.add([objMap.skolemize(), URIRef(R2RML.datatype), XSD[datatype]])
   #TODO: Add exceptions

def RefObjectMapGeneration(preObj,objNode,tmResource):
   global newg
   global subjectNode
   newg.add([preObj.skolemize(), URIRef(R2RML.objectMap), objNode])
   newg.add([objNode, RDF.type, URIRef(R2RML.RefObjectMap)])
   newg.add([objNode, URIRef(R2RML.parentTriplesMap), tmResource.skolemize()])

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

def resultsGenerator(outputfile):
   print("RML graph has %s statements." % len(newg))
   now = datetime.datetime.now()
   newg.add( (BNode(), URIRef("http://purl.org/dc/elements/1.1/created"), Literal(time.strftime(str(now.year)+"-"+str(now.month)+"-"+str(now.day))) ) ) 
   newg.serialize(outputfile,format='turtle')