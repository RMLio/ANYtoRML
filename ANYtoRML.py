import sys,getopt,logging
import RMLgenerator, CSVWtoRML

logging.basicConfig(filename='ANYtoRML.log',level=logging.DEBUG)

inputfile = ''
outputfile = ''

def main(argv):
   global inputfile, outputfile
   try:
      opts, args = getopt.getopt(argv,"hi:o:l:",["ifile=","ofile=","mlanguage"])
   except getopt.GetoptError:
      print 'python ANYtoRML.py -i <CSVW_mapDoc> -o <RML_mapDoc> -l <mappingLanguage>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print '\npython ANYtoRML.py -i <original_mapDoc> -o <RML_mapDoc> -l <mappingLanguage> \n'
         print '<original_mapDoc> Path to the original mapping document'
         print '<RML_mapDoc>      Path to the RML mapping document'
         print '<mappingLanguage> The mapping language used for the original mapping document (CSVW, D2RQL) \n'
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-o", "--ofile"):
         outputfile = arg
      elif opt in ("-l", "--mappingLanguage"):
         mappingLanguage = arg

   if(mappingLanguage == 'CSVW'):
      CSVWtoRML.CSVWtoRML(inputfile)

   RMLgenerator.resultsGeneration(outputfile)

if __name__ == "__main__":
    main(sys.argv[1:])