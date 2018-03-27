"""Module to extract data from docx files"""

import lxml.etree as ET
import zipfile
import re

OOXML_DOCUMENT_PATH = 'word/document.xml'
BOLD_OPEN = '<b>'
BOLD_CLOSE = '</b>'
ITALICS_OPEN = '<i>'
ITALICS_CLOSE = '</i>'
UNDERLINE_OPEN = '<u>'
UNDERLINE_CLOSE = '</u>'
OOXML_TAG = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
OOXML_BOLD = 'b'
OOXML_ITALICS = 'i'
OOXML_UNDERLINE = 'u'
OOXML_PARAGRAPH = 'p'
OOXML_PARAGRAPH_STYLE = 'pStyle'
OOXML_STYLE_VALUE = 'val'
OOXML_TEXT = 't'
OOXML_TEXT_RUN = 'r'
OOXML_STYLE_HEADING = '^Heading([0-9]+)$'
OOXML_STYLE_STRONG = 'Strong'
PLAIN_TEXT_PAGE_TAG = '[PAGE]: '
PLAIN_TEXT_GROUP_TAG = '[GROUP]{{{0}}}: '

def extract_xml_string(docx_path):
  """Receives the path of a docx file and returns a OOXML string"""

  zip_content = zipfile.ZipFile(docx_path)
  xml_string = zip_content.read(OOXML_DOCUMENT_PATH)

  return xml_string

#note that this function appends a new (blank) line in the end of the document.
def extract_plain_text(xml_string):
  """Receives an OOXML string and returns a plain text string with relevant
  data
  """

  root = ET.XML(xml_string)
  plain_text = ''
  bold = False
  italics = False
  underline = False
  #TODO: rename iterators
  for child in root.iter(OOXML_TAG + OOXML_PARAGRAPH): #Top element gets a paragraph tag
    for style_tag in child.iter(OOXML_TAG + OOXML_PARAGRAPH_STYLE):
      style = style_tag.get(OOXML_TAG + OOXML_STYLE_VALUE)
      heading = re.search(OOXML_STYLE_HEADING, style)
      if(heading):
        plain_text += PLAIN_TEXT_GROUP_TAG.format(heading.group(1))

    for tag in child.iter(OOXML_TAG + OOXML_TEXT_RUN): #if there is a child tag in the paragraph
      for childtag in tag.iter():
        style = childtag.get(OOXML_TAG + OOXML_STYLE_VALUE) #gets the type of style the tag is
        if(style == OOXML_STYLE_STRONG): # if the style is strong
          plain_text += PLAIN_TEXT_PAGE_TAG #add a strong tag

        if(childtag.tag == OOXML_TAG + OOXML_BOLD): # if the style is bold
          plain_text += BOLD_OPEN	#add a open bold tag
          bold = True

        if(childtag.tag == OOXML_TAG + OOXML_ITALICS): #if style is italics
          plain_text += ITALICS_OPEN	#add a open italics tag
          italics = True

        if(childtag.tag == OOXML_TAG + OOXML_UNDERLINE):	#if style is underline
          plain_text += UNDERLINE_OPEN #add open underline tag
          underline = True

        if(childtag.tag == OOXML_TAG + OOXML_TEXT): #if the tag is a text tag
          plain_text += childtag.text.encode('utf8')
          if(bold): #if the text is currently bold, add a close bold tag
            plain_text += BOLD_CLOSE
            bold = False

          if(italics): #if the text is currently italicized, add a italics end tag
            plain_text += ITALICS_CLOSE
            italics = False

          if(underline):#if the text is currently underlined, add a underline end tag
            plain_text += UNDERLINE_CLOSE
            underline = False

	
    plain_text += '\n' #add a new line at the end of each closing tag


  #removing MS word quotes
  
  #current fix
  unicodeCodes = ['\xe2\x80\x90', '\xe2\x80\x91', '\xe2\x80\x92', '\xe2\x80\x93', '\xe2\x80\x94', '\xe2\x80\x95', '\xe2\x80\x96', '\xe2\x80\x97', '\xe2\x80\x98', '\xe2\x80\x99', '\xe2\x80\x9a	', '\xe2\x80\x9b', '\xe2\x80\x9c', '\xe2\x80\x9d', '\xe2\x80\x9e', '\xe2\x80\x9f', '\xe2\x80\xa4', '\xe2\x80\xa5', '\xe2\x80\xa6', '\xe2\x80\xb8']
  textSubstitutions = ['-','-','-','-','-','-','|','_','\'','\'','\'','\'','"','"','"','"', '.', '..', '...', '^']
  
  #double quote fix
  #unicodeCodes = ['\xe2\x80\x90', '\xe2\x80\x91', '\xe2\x80\x92', '\xe2\x80\x93', '\xe2\x80\x94', '\xe2\x80\x95', '\xe2\x80\x96', '\xe2\x80\x97', '\xe2\x80\x98', '\xe2\x80\x99', '\xe2\x80\x9a	', '\xe2\x80\x9b', '\xe2\x80\x9c', '\xe2\x80\x9d', '\xe2\x80\x9e', '\xe2\x80\x9f', '\xe2\x80\xa4', '\xe2\x80\xa5', '\xe2\x80\xa6', '\xe2\x80\xb8']
  #textSubstitutions = ['-','-','-','-','-','-','|','_','\'','\'','\'','\'','&#x201C;','&#x201D;','"','"', '.', '..', '...', '^']
  
  #full fix
  #unicodeCodes = ['\xe2\x80\x90', '\xe2\x80\x91', '\xe2\x80\x92', '\xe2\x80\x93', '\xe2\x80\x94', '\xe2\x80\x95', '\xe2\x80\x96', '\xe2\x80\x97', '\xe2\x80\x98', '\xe2\x80\x99', '\xe2\x80\x9a	', '\xe2\x80\x9b', '\xe2\x80\x9c', '\xe2\x80\x9d', '\xe2\x80\x9e', '\xe2\x80\x9f', '\xe2\x80\xa4', '\xe2\x80\xa5', '\xe2\x80\xa6', '\xe2\x80\xb8']
  #textSubstitutions = ['-','-','-','-','-','-','|','_','&#x2019;','&#x201B;','&#x2019;','&#x201B;','&#x201C;','&#x201D;','"','"', '.', '..', '...', '^']
  
  counter = 0
  unicodeSubSize = len(unicodeCodes) - 1
  #if(plain_text.find("clone")):
	#plain_text = re.sub(" ","",plain_text)
  while(counter < unicodeSubSize):
    plain_text = re.sub(unicodeCodes[counter], textSubstitutions[counter], plain_text)
    counter += 1

  re.sub("[\\u2018\\u2019]", "'", plain_text)
  re.sub("[\\u201C\\u201D]", "\"", plain_text)
  return plain_text

