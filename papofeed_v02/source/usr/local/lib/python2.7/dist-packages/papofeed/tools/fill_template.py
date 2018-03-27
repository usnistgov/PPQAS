#!/usr/bin/python

import sys
import os
from jinja2 import FileSystemLoader
from jinja2.environment import Environment

WINDOWS_MAIN_DRIVE = 'C:/'

def fill(template_path, xml_path):
  env = Environment()
  #here is the windows problem: the root env!
  if(sys.platform != 'win32'):
    env.loader = FileSystemLoader('/')
  else:
    env.loader = FileSystemLoader(WINDOWS_MAIN_DRIVE)
    template_path = template_path[3:]
    xml_path = xml_path[3:]
  #if run directly, this is the correct env.loader TODO:__main__
  #env.loader = FileSystemLoader('.')
  tmpl = env.get_template(template_path)
  #print tmpl.render(xml_output=xml_path)

  temp_path = '_temp_file.xml'
  with open(temp_path, 'w') as temp_fd:
    temp_fd.write(tmpl.render(xml_output=xml_path))

  if(sys.platform == 'win32'):
    template_path = WINDOWS_MAIN_DRIVE + template_path
    xml_path = WINDOWS_MAIN_DRIVE + xml_path

  os.remove(xml_path)
  os.rename(temp_path, xml_path)

def clean_xml(xml_path):
  temp_path = '_temp_file.xml'
  with open(xml_path, 'r') as xml_file:
    lines = xml_file.readlines()
    with open(temp_path, 'w') as temp_fd:
      #7 to -4 is the range of elements we want to cut from the xml output of PaPo
      for line in lines[7:-4]:
        temp_fd.write(line)
  os.remove(xml_path)
  os.rename(temp_path, xml_path)


def main():
  if(len(sys.argv) != 3):
    print 'Usage: {0} template_file xml_file'.format(sys.argv[0])
  else:
    clean_xml(sys.argv[2])
    fill(sys.argv[1], sys.argv[2])

