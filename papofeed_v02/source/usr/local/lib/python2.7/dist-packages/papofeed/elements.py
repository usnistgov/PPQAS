"""Module with XML elements class representations."""

import re

__questions__ = []
__comments__ = []
__groups__ = []
__cdata__ = []
QUESTION_ID_FORMAT = '^q\.(\d+\.)*\d+$'
OPTION_ID_FORMAT = '^(q|c)\.(\d+\.)+[A-Z]$'
BNFMAPPING_ID_FORMAT = '^b\.\d+$'
COMMENT_ID_FORMAT = '^c\.(\d+\.)*\d+$'
INDENT_ID_FORMAT = '^d'
DISPLAY_WHEN_QUESTION_ID_FORMAT = '^q\.(\d+\.)*\d+(, *q\.(\d+\.)*\d+)*$'
DISPLAY_WHEN_OPTION_ID_FORMAT = '^(q|c)\.(\d+\.)+[A-Z](, *(q|c)\.(\d+\.)+[A-Z])*$'


class Question:

  """Single Questionaire Question

  id_attr: the question id. must be a 'q' followed by a sequence of digits and
  dots '.', always ending with a digit.
  indent_attr: an integer to multiply by 20 to get the # of pixels to indent by. Default = 2
  display_when_attr: a Question id or an option id.
  display_where_attr: [TODO: ASK CELIA]
  title_element: string
  text_elements: Text object list
  note_elements: Note object list
  bnf_mapping_elements: BNF_mapping object list
  instructions_elements: instructions object list
  response_elements: Response object list
  """

  def __init__(self,
      id_attr,
	  indent_attr=None,
      display_when_attr=None,
      display_where_attr=None,  
      title_element=None,
      text_elements=None,
      note_elements=None,
      bnf_mapping_elements=None,
      instructions_elements=None,
      response_elements=None,
      mod_response_elements=None,
      ):
    """Creates a Question and appends it to module variable __questions__."""

    if(not re.match(QUESTION_ID_FORMAT, id_attr)):
      raise Exception('Question id format does not match specification.')

    self.id_attr = id_attr
    if(indent_attr and not re.match(INDENT_ID_FORMAT, indent_attr)):
      raise Exception('indent_attr format does not match specification.')
	
    self.indent_attr = indent_attr
    if(display_when_attr and not
        re.match(DISPLAY_WHEN_OPTION_ID_FORMAT, display_when_attr) and not
        re.match(DISPLAY_WHEN_QUESTION_ID_FORMAT, display_when_attr)):
      raise Exception('display_when_attr format does not match specification.')

    self.display_when_attr = display_when_attr
    if(display_where_attr and not
        re.match(OPTION_ID_FORMAT, display_where_attr) and not
        re.match(QUESTION_ID_FORMAT, display_where_attr)):
      raise Exception('display_where_attr format does not match specification.')
    self.display_where_attr = display_where_attr
    self.title_element = title_element
    self.text_elements = text_elements or []
    self.note_elements = note_elements or []
    self.bnf_mapping_elements = bnf_mapping_elements or []
    self.instructions_elements = instructions_elements or []
    self.response_elements = response_elements or []
    self.mod_response_elements = mod_response_elements or []
	
    __questions__.append(self)

class Text:

  """XML text element

  content: content of the tag.
  type_attr: element's type attribute.
  """

  def __init__(self, content, type_attr=None):
    self.content = content
    self.type_attr = type_attr

class Note:

  """XML note element

  content: content of the tag.
  type_attr: element's type attribute.
  """

  def __init__(self, content, type_attr=None):
    self.content = content
    self.type_attr = type_attr

class BnfMapping:

  """XML BNF_mapping element

  id_attr: BNF ID
  content: content of the tag.
  type_attr: element's type attribute
  When attribute are just strings with options IDs
  """

  def __init__(self, id_attr, content=None, type_attr=None, when_attr=None):
    if(not re.match(BNFMAPPING_ID_FORMAT, id_attr)):
      raise Exception('BnfMapping id format does not match specification.')

    self.id_attr = id_attr
    self.content = content
    self.type_attr = type_attr
    self.when_attr = when_attr

class Instructions:

  """XML instructions element

  content: content of the tag.
  type_attr: element's type attribute.
  """

  def __init__(self, content, type_attr=None):
    self.content = content
    self.type_attr = type_attr

class Response:

  """XML response element

  type_attr: element's type attribute.
  text_elements: Text object list
  validation_elements: Validation object list
  memo_elements: Memo object list
  bnf_mapping_elements: BNF_mapping object list
  note_elements: Note object list
  option_elements: Option object list
  """

  def __init__(self,
      type_attr=None,
      text_elements=None,
      validation_elements=None,
	  memo_elements=None,
	  textBox_elements=None,
      bnf_mapping_elements=None,
      note_elements=None,
      option_elements=None):
    self.type_attr = type_attr
    self.text_elements = text_elements or []
    self.validation_elements = validation_elements or []
    self.memo_elements = memo_elements or []
    self.textBox_elements = textBox_elements or []
    self.bnf_mapping_elements = bnf_mapping_elements or []
    self.note_elements = note_elements or []
    self.option_elements = option_elements or []

class Option:

  """XML option element

  id_attr: the option id. must be a question id followed by a '.' and an upper
  case letter.
  clone_attr: element's clone attribute
  text_elements: Text object list
  bnf_mapping_elements: BNF_mapping object list
  validation_element: Validation object
  """

  def __init__(self,
      id_attr,
      clone_attr=None,
      text_element=None,
      bnf_mapping_elements=None,
      note_element=None,
      validation_element=None):
    if(not re.match(OPTION_ID_FORMAT, id_attr)):
      raise Exception('Option id format does not match specification.')

    self.id_attr = id_attr
    self.clone_attr = clone_attr
    self.text_element = text_element
    self.bnf_mapping_elements = bnf_mapping_elements or []
    self.note_element = note_element
    self.validation_element = validation_element

	
class Validation:

  """XML validation element

  content: content of the tag.
  type_attr: element's type attribute.
  """

  def __init__(self, type_attr=None, content_dict=None):
    self.type_attr = type_attr
    self.content = content_dict or {}

class textBox:
  """XML textBox element

  content: content of the tag.
  type_attr: element's type attribute.
  """
  def __init__(self, type_attr=None, content_dict=None):
    self.type_attr = type_attr
    self.content = content_dict or {}
	
class Memo:
  """XML Memo element

  content: content of the tag.
  type_attr: element's type attribute.
  """
  def __init__(self, type_attr=None, content_dict=None):
    self.type_attr = type_attr
    self.content = content_dict or {}	
	
class Comment:

  """additional_comments question

  id_attr: the comment id. must be a 'c' followed by a sequence of digits and
  dots '.', always ending with a digit.
  indent_attr: a indent attribute
  display_when_attr: a Question id or an option id.
  display_where_attr: [TODO: ASK CELIA]
  text_elements: Text object list
  note_elements: Note object list
  instructions_elements: instructions object list
  response_elements: Response object list
  """

  def __init__(self,
      id_attr,
      indent_attr=None,
	  display_when_attr=None,
      display_where_attr=None,
      text_elements=None,
      note_elements=None,
      instructions_elements=None,
      response_elements=None,
	  mod_response_elements=None,
      ):
    """Creates a comment and appends it to module variable __comments__."""

    if(not re.match(COMMENT_ID_FORMAT, id_attr)):
      raise Exception('comment id format does not match specification.')
    self.id_attr = id_attr
	
    if(indent_attr and not re.match(INDENT_ID_FORMAT, indent_attr)):
      raise Exception('indent_attr format does not match specification.')
    self.indent_attr = indent_attr
	
    if(display_when_attr and not
        re.match(OPTION_ID_FORMAT, display_when_attr) and not
        re.match(COMMENT_ID_FORMAT, display_when_attr)):
      raise Exception('display_when_attr format does not match specification.')
    self.display_when_attr = display_when_attr
   
    if(display_where_attr and not
        re.match(OPTION_ID_FORMAT, display_where_attr) and not
        re.match(COMMENT_ID_FORMAT, display_where_attr)):
      raise Exception('display_where_attr format does not match specification.')
    self.display_where_attr = display_where_attr
    
    self.text_elements = text_elements or []
    self.note_elements = note_elements or []
    self.instructions_elements = instructions_elements or []
    self.response_elements = response_elements or []
    self.mod_response_elements = mod_response_elements or []
    #TODO: add title element to tests and to constructor
    self.title_element = None
    __comments__.append(self)

class Group:

  """XML group element

  level_attr: XML Group level attribute
  title_attr: XML Group title attribute
  comment_ref_attr: XML Group comment_ref attribute
  next_attr: XML Group next attribute
  back_attr: XML Group back attribute
  instructions_elements: instructions object list
  text_elements: Text object list
  page_elements: Page object list
  group_elements: Group object list
  """

  def __init__(self,
      level_attr,
      title_attr=None,
      comment_ref_attr=None,
      next_attr=None,
      back_attr=None,
      instructions_elements=None,
      text_elements=None,
      page_elements=None,
      group_elements=None
      ):
    self.level_attr = int(level_attr)
    self.comment_ref_attr = comment_ref_attr
    self.title_attr = title_attr
    self.next_attr = next_attr
    self.back_attr = back_attr
    self.instructions_elements = instructions_elements or []
    self.text_elements = text_elements or []
    self.page_elements = page_elements or []
    self.group_elements = group_elements or []
    if(self.level_attr == 1):
      __groups__.append(self)

class Page:

  """XML page element

  title_attr: XML Page title attribute
  comment_ref_attr: XML Page comment_ref attribute
  next_attr: XML Page next attribute
  back_attr: XML Page back attribute
  instructions_elements: instructions object list
  text_elements: Text object list
  include_elements: include object list
  """

  def __init__(self,
      title_attr=None,
      comment_ref_attr=None,
      next_attr=None,
      back_attr=None,
      instructions_elements=None,
      text_elements=None,
      include_elements=None
      ):
    self.comment_ref_attr = comment_ref_attr
    self.title_attr = title_attr
    self.next_attr = next_attr
    self.back_attr = back_attr
    self.instructions_elements = instructions_elements or []
    self.text_elements = text_elements or []
    self.include_elements = include_elements or []

class Include:

  """XML include element

  qref_attr: XML include qref attribute
  """

  def __init__(self, qref_attr=None):
    self.qref_attr = qref_attr

