import RMLgenerator
import sys,getopt,logging
import rdflib, re, time, datetime

from rdflib import Graph, Namespace, URIRef, BNode, RDF, Literal, plugin
from rdflib.namespace import RDF, XSD
from rdflib.serializer import Serializer

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
   column = g.value(subject = node, predicate = CSVW.propertyUrl)

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

      #Extract the table's URL
      sources = g.objects(tableValue.table, URIRef(CSVW.url))

      for source in sources:
         #TODO: Replace the following with CSVW Source description
         #source = URIRef(source)
         print "Source " + source
         #source = locateTable(tableValue)
         source = Literal(source)

         logSource = logicalSourceGeneration(source)

         RMLgenerator.TriplesMapGeneration(tmNode,logSource)

         print "Generating Subject Map for table schema " + str(tableValue.tableSchema)
         #generate Blank node for Subject Map
         subjMapBN = BNode().skolemize()
         #Generate Subject Map
         RMLgenerator.BlankNodeSubjectMapGeneration(tmNode,subjMapBN)

         print "Generating Predicate Object Maps for table schema " + str(tableValue.tableSchema)
         columns = g.value(subject = tableValue.tableSchema, predicate = URIRef(CSVW.column))

         #If table schema is in separate file
         if columns == None:
            table = g.value(predicate = URIRef(CSVW.url), object = Literal(source))
            tableSchema = g.value(subject = table, predicate = URIRef(CSVW.tableSchema))

            #g =rdflib.Graph()
            g.parse(tableSchema, format='json-ld')

            columns = g.triples((None, URIRef(CSVW.column),None),)
            for s,p,o in columns:
               columns = o

         nextFirst = columns
            
         while nextFirst:
            column = None
            preObj = None
            node = g.value(subject = nextFirst, predicate = RDF.first)

            column = retrieveColumn(source,node)
                     
            if column:
               preObj = BNode().skolemize()
               RMLgenerator.PredicateObjectMapGeneration(tmNode,preObj)

               #print "Generating Predicate Map..."
               RMLgenerator.PredicateMapGeneration(column,preObj)

               #print "Generating Object Map..."
               #Extract the title that points to the corresponding column to generate the Object Map
               objectValues = g.objects(node,URIRef(CSVW.title))
               for objectValue in objectValues:
                  objMap = RMLgenerator.ObjectMapGeneration(Literal(objectValue),preObj,'reference-valued')
                  if (node, CSVW.datatype, None ) in g:
                     #print "Checking for datatype..."
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
                        RMLgenerator.DatatypeGeneration(datatype,objMap)
               elif (node, URIRef(CSVW.valueUrl), None) in g:
                  objectValues = g.objects(node,URIRef(CSVW.valueUrl))
                  for objectValue in objectValues:
                     objectValueBN = BNode().skolemize()
                     objMap = RMLgenerator.ObjectMapGeneration(Literal(objectValue),preObj,'template-valued')

            nextFirst = g.value(subject = nextFirst, predicate = RDF.rest)
            




               

         
            


            