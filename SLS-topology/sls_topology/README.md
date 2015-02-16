ATLAS Service Monitoring - SLS topology
=====

Topology processes a configurable subset of all SLS service XMLs from the directory specified in the 
configuration file, and dumps the topology in a json file, and visualizes it as a PDF or PNG files. 

Dependencies: Using BeautifulSoup library to parse XML files.
   ``` 
# pip install BeautifulSoup   # version 3.2.0
  ```
Using graphviz library to visualize directed graphs.
   ``` 
# pip install graphviz   # version 0.3.4
  ```


Configuration
-----
General configuration file: sls\_topology/settings/settings-sls-topology.cfg.

  Data.status is a configuration flag which determines whether the output files 
  will or will not have UTC timestamp in the filename. If status=prod, the 
  timestamp is left out from the output file name. Otherwise, the timestamp is 
  part of the output file name. 
  ```
[Data]
### status=prod: no timestamp in the output file name
### status=devel: timestamp is part of the output file name
status = prod
# status = devel
 
  ```

  Data.dir\_source\_xml specifies base directory with SLS service XML files 
  (retrieved by the SLS Scraper). 
  ```
[Data]
### dir_source_xml: directory with the service XML files
dir_source_xml = /data/jschovan/slsmon/download/sls/xml/
 
  ```

  Data.dir\_output specifies directory where the topology output files will 
  be stored. 
  ```
[Data]
### dir_output: directory to store output files: .json, .dot, .pdf, .png
dir_output = /data/jschovan/slsmon/topology/output/
 
  ```

  Data.groups specifies list of service groups to be plotted. A single service 
  group is a relative directory path as a subdirectory in Data.dir\_source\_xml, 
  e.g. ServicesForATLAS/ADC\_CS. Output topology file for a single group then 
  contains parent <= child directed graph representing services and subservices 
  listed the XML files of the single group directory, leaving out subdirectories
  of this single group (e.g. subgroup ServicesForATLAS/ADC\_CS/ATLAS-Frontier 
  of group ServicesForATLAS/ADC\_CS will be displayed as a node in the ADC\_CS 
  topology plots, and will be displayed as a more detailed graph in the 
  ATLAS-Frontier topology plots). 

  Too large service groups result in large PNG topology plots, that can be hard 
  to read, please keep that in mind in specifying granularity of your 
  service groups. 
  ```
[Data]
### dir_output: directory to store output files: .json, .dot, .pdf, .png
dir_output = /data/jschovan/slsmon/topology/output/
 
  ```

  Document.tags specifies which XML tags will be translated into SLS topology 
  json output. Tags can be structured. Parent tag and children tags are 
  separated with a colon, children tags are separated with a pipe.
  ```
[Document]
### tags: list of XML tags to be parsed and stored in the output .json file
###    Parent tag is separated from children tags with a colon, 
###        e.g. parent:child1
###    Children tags are separated with a pipe,
###        e.g. parent:child1|child2|child3
tags = id,fullname,shortname,type,searchable,visibleinsubservices,site,group,
 email,webpage,alarmpage,staticxmllocation,datasource:url|metaservice,
 availabilitythresholds:threshold,willbenotified,emailorsms,dependency,
 servicemanagers:servicemanager,staticxmllocation,subservices:subservice

  ```


How to run
-----
  ```
# cd sls\_topology/
# ls
__init__.py  README.md  settings  sls_topology.py
# export PYTHONPATH=$PWD:$PYTHONPATH
# python sls\_topology.py
  ```


