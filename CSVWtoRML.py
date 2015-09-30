import RMLgenerator
import sys,getopt,logging
import rdflib, re, time, datetime

from rdflib import Graph, Namespace, URIRef, BNode, RDF, Literal, plugin
from rdflib.namespace import RDF, XSD
from rdflib.serializer import Serializer

logging.basicConfig(filename='CSVWtoRML.log',level=logging.DEBUG)

CSVW = Namespace("http://www.w3.org/ns/csvw#")
QL   = Namespace("http://semweb.mmlab.be/ns/ql#")

g=rdflib.Graph()

def CSVWtoRML(inputfile):
   g.parse(inputfile, format='json-ld')
   print("CSVW graph has %s statements." % len(g))

   #Extract the table's URL
   sources = g.objects(None, URIRef(CSVW.url))
   if sources:
      #TODO: Replace the following with CSVW Source description   
      source = URIRef(sources.next())

   #extract table URL to generate the Logical Source
   logSource = BNode().skolemize()
   #Generate the Logical Source
   RMLgenerator.LogicalSourceGeneration(logSource,source)

   #Generate Reference Formulation
   ReferenceFormulationValue = URIRef(QL.CSV)
   RMLgenerator.ReferenceFormulationGeneration(logSource, ReferenceFormulationValue)

   tmValues = g.query(
      """SELECT DISTINCT ?aboutUrl
      WHERE {
      ?tmValue <http://www.w3.org/ns/csvw#aboutUrl> ?aboutUrl .
      }""")

   for tmValue in tmValues:

      print "Generating Triples Maps..."
      strTmValue = str(tmValue.aboutUrl)
      #extract about URL to generate Triples Map URI
      uriTmValue = URIRef(strTmValue.replace('{','').replace('}',''))
      RMLgenerator.TriplesMapGeneration(uriTmValue,logSource)

      print "Generating Subject Maps..."
      #generate Blank node for Subject Map
      subjMapBN = BNode().skolemize()
      #Generate Subject Map
      RMLgenerator.SubjectMapGeneration(uriTmValue,subjMapBN)
      #Subject Map template generated according to csvw:aboutURL
      RMLgenerator.SubjectMapTemplateGeneration(subjMapBN,strTmValue)

      #Extract columns to turn them into Predicate Object Maps
      for preObj,predicate,object in g.triples( (None, URIRef(CSVW.column), None) ):
         print "Generating Predicate Object Maps..."
         preObj = BNode().skolemize()
         RMLgenerator.PredicateObjectMapGeneration(uriTmValue,preObj)

         #TODO: Change RDF.first to iterate over the available predicates
         #Extract each column
         column = g.value(subject = object, predicate = RDF.first)
         print "column " + str(column)

         #Extract the property URL to generate the Predicate Map
         predicateValues = g.objects(column,URIRef(CSVW.propertyUrl))

         #For each property URL, add a value
         for predicateValue in predicateValues:
            RMLgenerator.PredicateMapGeneration(predicateValue,preObj)
            print 'predicate value ' + str(predicateValue)

            #If rdf:type, generate rr:class
            if(predicateValue == RDF.type):
               types = g.objects(column,URIRef(CSVW.valueUrl))
               for type in types:
                  RMLgenerator.ClassGeneration(subjMapBN,URIRef(type))

            #Extract the title that points to the corresponding column to generate the Object Map
            objectValues = g.objects(column,URIRef(CSVW.title))
            for objectValue in objectValues:
               objMap = RMLgenerator.ObjectMapGeneration(Literal(objectValue),preObj,'reference')
               if (column, CSVW.datatype, None ) in g:
                  datatype = g.value(column, URIRef(CSVW.datatype))
                  datatypeValue = g.value(datatype, CSVW.base)
                  RMLgenerator.DatatypeGeneration(datatypeValue,objMap)

            objectValues = g.objects(column,URIRef(CSVW.valueUrl))
            for objectValue in objectValues:
               print 'object value ' + objectValue
               objectValueBN = BNode().skolemize()
               print 'object value blank node ' + objectValueBN
               if(predicateValue != RDF.type):
                  tmResource = URIRef(str(objectValue).replace('-{_row}',''))
                  print "tmResource " + tmResource
                  RMLgenerator.RefObjectMapGeneration(preObj, objectValueBN,tmResource)
                  RMLgenerator.TriplesMapGeneration(tmResource,logSource)
               else:
                  objMap = RMLgenerator.ObjectMapGeneration(URIRef(objectValue),preObj,'constant')
               #SubjectMapGeneration(tmResource)