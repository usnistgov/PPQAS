#!/usr/bin/python

import os
import sys
import re
from papofeed import extractor, feed, elements, toxml

def main():
  if(len(sys.argv) == 3):
    docx_file = sys.argv[1]
    xml_output = sys.argv[2]
  else:
    docx_file = 'questionnaire.docx'
    xml_output = 'output.xml'

  xml = extractor.extract_xml_string(docx_file)
  plain_text = extractor.extract_plain_text(xml)

  #uncomment if a plain text file is needed for debugging purposes
  with open(xml_output + '_err.txt', 'w') as fd:
    fd.write(plain_text)
  ##

  feed.parse(plain_text)
  toxml.populate()
  toxml.write(xml_output)

  #if everything runs ok, removes the plain.txt file
  #uncomment if the plain text file is needed
  os.remove(xml_output + '_err.txt')

  #removing '[PAGE]: ' from output file
  with open(xml_output, 'r') as raw_output:
    with open('output.xml.new', 'w') as output:
      for line in raw_output.readlines():
        output.write(re.sub('\[PAGE\]: ','',line))

  os.remove(xml_output)
  os.rename('output.xml.new', xml_output)

