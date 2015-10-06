import RMLgenerator
import sys,getopt,logging
import rdflib, re, time, datetime

from rdflib import Graph, Namespace, URIRef, BNode, RDF, Literal, plugin
from rdflib.namespace import RDF, XSD
from rdflib.serializer import Serializer

logging.basicConfig(filename='/media/andimou/723A1FC53A1F856F/Ubuntu_Documents/MappingDocs/ANYtoRML/log/CSVWtoRML.log', filemode='w', level=logging.DEBUG)
#logging.setLevel(logging.INFO)

CSVW = Namespace("http://www.w3.org/ns/csvw#")
QL   = Namespace("http://semweb.mmlab.be/ns/ql#")

g=rdflib.Graph()

def retrieveTableSchema():
   tableValues = g.query(
      """SELECT DISTINCT ?table ?tableSchema
      WHERE {
      ?table <http://www.w3.org/ns/csvw#tableSchema> ?tableSchema .
      }""")
   return tableValues


def locateTable(tableValue):
   #TODO: Replace the following with CSVW Source description
   source = g.value(subject = tableValue.table, object = URIRef(CSVW.url))
   print "source " + source
   return URIRef(source)



def logicalSourceGeneration(source):
   #extract table URL to generate the Logical Source
      logSource = BNode().skolemize()
      #Generate the Logical Source
      RMLgenerator.LogicalSourceGeneration(logSource,source)

      #Generate Reference Formulation
      ReferenceFormulationValue = URIRef(QL.CSV)
      RMLgenerator.ReferenceFormulationGeneration(logSource, ReferenceFormulationValue)

      return logSource


def retrieveColumn(source,node):
   column = None
   #column = g.value(subject = node, predicate = CSVW.propertyUrl)

   if not column:
      column = g.value(subject = node, predicate = CSVW.name)
      if column:
         #column = source + "#" + column
         column = "http://example.org/countries.csv#" + column

   return column


def datatypeGeneration(node, objMap):
   datatype = g.value(node, URIRef(CSVW.datatype))
   datatypeValue = g.value(datatype, CSVW.base)
   if datatypeValue:
      datatype = URIRef("http://www.w3.org/2001/XMLSchema#" + datatypeValue)

   if(datatype):
      RMLgenerator.DatatypeGeneration(datatype,objMap)


def CSVWtoRML(inputfile):
   logging.info('INFO')
   logging.debug('DEBUG')
   logging.error('ERROR')

   logging.debug("CSVWtoRML has started.")
   g.parse(inputfile, format='json-ld')
   print("CSVW graph has %s statements." % len(g))

   enumerator = 0

   #TODO: Extend to work for table groups too
   print "Retrieving table schema..."
   tableValues = retrieveTableSchema()
      

   for tableValue in tableValues:
      tmValue = "http://example.com/TriplesMap#" + str(enumerator)
      enumerator = enumerator + 1
      #Triples Map node
      tmNode = URIRef(tmValue)

      print "Retrieving individual table..."
      #source = locateTable(tableValue)

      #Extract the table's URL
      sources = g.objects(tableValue.table, URIRef(CSVW.url))

      for source in sources:
         #TODO: Replace the following with CSVW Source description
         #source = URIRef(source)
         source = Literal(source)

         logSource = logicalSourceGeneration(source)

         logging.debug('Generating TriplesMap...')
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

            print "Retrieving column..."
            column = retrieveColumn(source,node)
                     
            if column:
               preObj = BNode().skolemize()
               RMLgenerator.PredicateObjectMapGeneration(tmNode,preObj)

               print "Generating Predicate Map..."
               RMLgenerator.PredicateMapGeneration(column,preObj)

               print "Generating Object Map..."
               #Extract the title that points to the corresponding column to generate the Object Map
               objectValues = g.objects(node,URIRef(CSVW.title))
               for objectValue in objectValues:
                  
                  objMap = RMLgenerator.ObjectMapGeneration(Literal(objectValue),preObj,'reference-valued')
                  if (node, CSVW.datatype, None ) in g:
                     print "Checking for datatype..."
                     datatypeGeneration(node, objMap)
                     
               if ((node, URIRef(CSVW.valueUrl), None) not in g):
               #if ((node, URIRef(CSVW.title), None) not in g) and ((node, URIRef(CSVW.valueUrl), None) not in g):
                  objectValues = g.objects(node,URIRef(CSVW.name))
                  for objectValue in objectValues:
                     objectValueBN = BNode().skolemize()

                     objMap = RMLgenerator.ObjectMapGeneration(Literal(objectValue),preObj,'reference-valued')
                     datatype = g.value(node, URIRef(CSVW.datatype))
                     if (datatype, CSVW.base, None ) in g:
                        datatype = g.value(node, URIRef(CSVW.base))
                     if objMap and datatype:
                        #datatype = g.value(node, URIRef(CSVW.datatype))
                        #if(datatype):
                        print "Checking for datatype..."
                        RMLgenerator.DatatypeGeneration(datatype,objMap)
               elif (node, URIRef(CSVW.valueUrl), None) in g:
                  objectValues = g.objects(node,URIRef(CSVW.valueUrl))
                  for objectValue in objectValues:
                     objectValueBN = BNode().skolemize()
                     objMap = RMLgenerator.ObjectMapGeneration(Literal(objectValue),preObj,'template-valued')

            nextFirst = g.value(subject = nextFirst, predicate = RDF.rest)
            print "next..."
            




               

         
            


            