import os
import re
from papofeed import extractor, feed, elements, toxml

docx_file = ('questionnaire.docx')
xml = extractor.extract_xml_string(docx_file)
plain_text = extractor.extract_plain_text(xml)
#uncomment if a plain text file is needed for debugging purposes
#with open('plain.txt', 'w') as fd:
  #fd.write(plain_text)

feed.parse(plain_text)
toxml.populate()
toxml.write('output.xml')
#removing '[PAGE]: ' from output file
with open('output.xml', 'r') as raw_output:
  with open('output.xml.new', 'w') as output:
    for line in raw_output.readlines():
      output.write(re.sub('\[PAGE\]: ','',line))

os.remove('output.xml')
os.rename('output.xml.new', 'output.xml')

