ANYtoRML
=============

Python script that converts mapping documents in different mapping languages to RML mapping documents

Usage
-----
You can run a conversion by executing the following command:
    
    python ANYtoRML.py -i <inputFile> -o <ouptutFile> -l <mappingLanguage>

With 
    
    <inputFile>  = The original mapping document 
    <outputFile> = The corresponding RML mapping document
    <mappingLanguage> = The original mapping language (currentl D2RQL,CSVW)


Requirements
------------
ANYtoRML requires the [rdflib-jsonld](https://github.com/RDFLib/rdflib-jsonld) plugin.

More Information
----------------

More information about the solution can be found at http://rml.io

This application is developed by Multimedia Lab http://www.mmlab.be

Copyright 2015, Multimedia Lab - Ghent University - iMinds

License
-------

The RMLProcessor is released under the terms of the [MIT license](http://opensource.org/licenses/mit-license.html).
