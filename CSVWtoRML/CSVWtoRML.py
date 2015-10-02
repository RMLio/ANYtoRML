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

   enumerator = 0

   tableValues = g.query(
      """SELECT DISTINCT ?table ?tableSchema
      WHERE {
      ?table <http://www.w3.org/ns/csvw#tableSchema> ?tableSchema .
      }""")

   for tableValue in tableValues:
      tmValue = "http://example.com/TriplesMap#" + str(enumerator)
      enumerator = enumerator + 1
      tmNode = URIRef(tmValue)

      #Extract the table's URL
      sources = g.objects(tableValue.table, URIRef(CSVW.url))

      for source in sources:
         #print "source " + source
         #TODO: Replace the following with CSVW Source description
         source = URIRef(source)

         #extract table URL to generate the Logical Source
         logSource = BNode().skolemize()
         #Generate the Logical Source
         RMLgenerator.LogicalSourceGeneration(logSource,source)

         #Generate Reference Formulation
         ReferenceFormulationValue = URIRef(QL.CSV)
         RMLgenerator.ReferenceFormulationGeneration(logSource, ReferenceFormulationValue)

         print "Generating Triples Maps..."
         RMLgenerator.TriplesMapGeneration(tmNode,logSource)

         print "Generating Subject Maps..."
         #generate Blank node for Subject Map
         subjMapBN = BNode().skolemize()
         #Generate Subject Map
         RMLgenerator.BlankNodeSubjectMapGeneration(tmNode,subjMapBN)

         print "Generating Predicate Object Maps..."
         columns = g.value(subject = tableValue.tableSchema, predicate = URIRef(CSVW.column))
         nextFirst = columns
         
         while nextFirst:
            column = None
            preObj = None
            node = g.value(subject = nextFirst, predicate = RDF.first)
            column = g.value(subject = node, predicate = CSVW.propertyUrl)
            
            if not column:
               column = g.value(subject = node, predicate = CSVW.name)
               if column:
                  column = source + "#" + column
                  
            if column:
               preObj = BNode().skolemize()
               RMLgenerator.PredicateObjectMapGeneration(tmNode,preObj)
               RMLgenerator.PredicateMapGeneration(column,preObj)

               #Extract the title that points to the corresponding column to generate the Object Map
               objectValues = g.objects(node,URIRef(CSVW.title))
               for objectValue in objectValues:
                  print "object value " + str(objectValue)

                  objMap = RMLgenerator.ObjectMapGeneration(Literal(objectValue),preObj,'reference-valued')
                  if (node, CSVW.datatype, None ) in g:
                     datatype = g.value(node, URIRef(CSVW.datatype))
                     datatypeValue = g.value(datatype, CSVW.base)
                     if datatypeValue:
                        datatype = URIRef("http://www.w3.org/2001/XMLSchema#" + datatypeValue)
                     print "datatype " + str(datatype)
                     if(datatype):
                        RMLgenerator.DatatypeGeneration(datatype,objMap)

                  
               if ((node, URIRef(CSVW.title), None) not in g) and ((node, URIRef(CSVW.valueUrl), None) not in g):
                  print "here?"
                  objectValues = g.objects(node,URIRef(CSVW.name))
                  for objectValue in objectValues:
                     objectValueBN = BNode().skolemize()
                     objectivo = Literal(objectValue)
                     print "preObj " + preObj
                     objMap = RMLgenerator.ObjectMapGeneration(objectivo,preObj,'reference-valued')
                     if objMap and (node, CSVW.datatype, None ) in g:
                        datatype = g.value(node, URIRef(CSVW.datatype))
                        if(datatype):
                           RMLgenerator.DatatypeGeneration(datatype,objMap)
               elif (node, URIRef(CSVW.valueUrl), None) in g:
                  objectValues = g.objects(node,URIRef(CSVW.valueUrl))
                  for objectValue in objectValues:
                     objectValueBN = BNode().skolemize()
                     objMap = RMLgenerator.ObjectMapGeneration(Literal(objectValue),preObj,'template-valued')

            nextFirst = g.value(subject = nextFirst, predicate = RDF.rest)
            print "next..."
            




               

         
            


            