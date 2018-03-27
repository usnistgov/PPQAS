"""Module to generate the XML output file from the elements module lists
objects"""

import lxml.etree as ET
from papofeed import elements

ROOT = ET.Element('questionnaire')
TITLE = ET.SubElement(ROOT, 'title')
XMLVERSION = ET.SubElement(ROOT, 'xmlversion')
QAVERSION = ET.SubElement(ROOT, 'qaversion')
BNFVERSION = ET.SubElement(ROOT, 'BNFversion')
INDENT_PX = ET.SubElement(ROOT, 'indent_px')
INDEX = ET.SubElement(ROOT, 'index')
QUESTIONS = ET.SubElement(ROOT, 'questions')
ADDITIONAL_COMMENTS = ET.SubElement(ROOT, 'additional_comments')
STATIC_TEXT = ET.SubElement(ROOT, 'static_text')
GENERAL_COMMENTS = ET.SubElement(ROOT, 'general_comments')
DEMOGRAPHICS_SURVEY = ET.SubElement(ROOT, 'demographics_survey')

def populate():
  """Uses the elements module lists to feed a XML tree"""

  #question
  print("hello")
  for question in elements.__questions__:
    question_element = ET.SubElement(QUESTIONS, 'question')
    question_element.set('id', question.id_attr)
    if(question.indent_attr): 
      question_element.set('indent', question.indent_attr)
    if(question.display_when_attr):
      question_element.set('display_when', question.display_when_attr)

    if(question.display_where_attr):
      question_element.set('display_where', question.display_where_attr)
    
	#title
    if(question.title_element):
      question_title = ET.SubElement(question_element, 'title')
      question_title.text = question.title_element

    #text
    for text_element in question.text_elements:
      question_text = ET.SubElement(question_element, 'text')
      if(text_element.type_attr):
        question_text.set('type', text_element.type_attr)

      question_text.text = text_element.content

    #note
    for note_element in question.note_elements:
      question_note = ET.SubElement(question_element, 'note')
      if(note_element.type_attr):
        question_note.set('type', note_element.type_attr)

      question_note.text = note_element.content
	
    #bnf
    for bnf_mapping_element in question.bnf_mapping_elements:
      question_bnf_mapping = ET.SubElement(question_element, 'BNF_mapping')
      question_bnf_mapping.set('id', bnf_mapping_element.id_attr)
      if(bnf_mapping_element.type_attr):
        question_bnf_mapping.set('type', bnf_mapping_element.type_attr)

      if(bnf_mapping_element.when_attr):
        question_bnf_mapping.set('when', bnf_mapping_element.when_attr)

      question_bnf_mapping.text = bnf_mapping_element.content

    #instructions
    for instructions_element in question.instructions_elements:
      question_instructions = ET.SubElement(question_element, 'instructions')
      if(instructions_element.type_attr):
        question_instructions.set('type', instructions_element.type_attr)

      question_instructions.text = instructions_element.content

    #response
    for response_element in question.response_elements:
      question_response = ET.SubElement(question_element, 'response')
      if(response_element.type_attr):
        question_response.set('type', response_element.type_attr)
      #response->text
      for text_element in response_element.text_elements:
        response_text = ET.SubElement(question_response, 'text')
        if(text_element.type_attr):
          response_text.set('type', text_element.type_attr)

        response_text.text = text_element.content

      #response->validation
      for validation_element in response_element.validation_elements:
        response_validation = ET.SubElement(question_response, 'validation')
        if(validation_element.type_attr):
          response_validation.set('type', validation_element.type_attr)

        for validation_key in validation_element.content.iterkeys():
          response_validation_element = ET.SubElement(response_validation, validation_key)
          response_validation_element.text = validation_element.content[validation_key]
      
      #response->textBox
      for textBox_element in response_element.textBox_elements:
		response_textBox = ET.SubElement(question_response, 'textBox') #creates the memo subtree
		if(textBox_element.type_attr):
		  response_memo.set('type', textBox_element.type_attr)
		
		for textBox_key in textBox_element.content.iterkeys():
		  response_textBox_element = ET.SubElement(response_textBox, textBox_key)
		  response_textBox_element.text = textBox_element.content[textBox_key]
	  
	  #response->memo
      for memo_element in response_element.memo_elements:
		response_memo = ET.SubElement(question_response, 'memo') #creates the memo subtree
		if(memo_element.type_attr):
		  response_memo.set('type', memo_element.type_attr)
		
		for memo_key in memo_element.content.iterkeys():
		  response_memo_element = ET.SubElement(response_memo, memo_key)
		  response_memo_element.text = memo_element.content[memo_key]  
	  
      #response->bnf
      for bnf_mapping_element in response_element.bnf_mapping_elements:
        response_bnf_mapping = ET.SubElement(question_response, 'BNF_mapping')
        response_bnf_mapping.set('id', bnf_mapping_element.id_attr)
        if(bnf_mapping_element.type_attr):
          response_bnf_mapping.set('type', bnf_mapping_element.type_attr)

        if(bnf_mapping_element.when_attr):
          response_bnf_mapping.set('when', bnf_mapping_element.when_attr)

        response_bnf_mapping.text = bnf_mapping_element.content

      #response->note
      for note_element in response_element.note_elements:
        response_note = ET.SubElement(question_response, 'note')
        if(note_element.type_attr):
          response_note.set('type', note_element.type_attr)

        response_note.text = note_element.content


	  #response->option
      for option_element in response_element.option_elements:
        response_option = ET.SubElement(question_response, 'option')
        response_option.set('id', option_element.id_attr)
        if(option_element.clone_attr):
          response_option.set('clone', option_element.clone_attr)

        #response->option->text
        if(option_element.text_element):
          response_option_text = ET.SubElement(response_option, 'text')
          if(option_element.text_element.type_attr):
            response_option_text.set('type', option_element.text_element.type_attr)

          response_option_text.text = option_element.text_element.content

        #response->option->bnf
        if(option_element.bnf_mapping_elements):
          for bnf_mapping_element in option_element.bnf_mapping_elements:
            response_option_bnf_mapping = ET.SubElement(response_option, 'BNF_mapping')
            response_option_bnf_mapping.set('id', bnf_mapping_element.id_attr)
            if(bnf_mapping_element.type_attr):
              response_option_bnf_mapping.set('type', bnf_mapping_element.type_attr)

            if(bnf_mapping_element.when_attr):
              response_option_bnf_mapping.set('when', bnf_mapping_element.when_attr)

            response_option_bnf_mapping.text = bnf_mapping_element.content

        #response->option->note
        if(option_element.note_element):
          response_option_note = ET.SubElement(response_option, 'note')
          if(option_element.note_element.type_attr):
            response_option_note.set('type', option_element.note_element.type_attr)

          response_option_note.text = option_element.note_element.content

        #response->option->validation
        if(option_element.validation_element):
          response_option_validation = ET.SubElement(response_option, 'validation')
          if(option_element.validation_element.type_attr):
            response_option_validation.set('type', option_element.validation_element.type_attr)

          for validation_key in option_element.validation_element.content.iterkeys():
            response_option_validation_element = ET.SubElement(response_option_validation, validation_key)
            response_option_validation_element.text = option_element.validation_element.content[validation_key]

  #comment
  for comment in elements.__comments__:
    comment_element = ET.SubElement(ADDITIONAL_COMMENTS, 'comments')
    comment_element.set('id', comment.id_attr)
    if(comment.display_when_attr):
      comment_element.set('display_when', comment.display_when_attr)

    if(comment.display_where_attr):
      comment_element.set('display_where', comment.display_where_attr)

    #text
    for text_element in comment.text_elements:
      comment_text = ET.SubElement(comment_element, 'text')
      if(text_element.type_attr):
        comment_text.set('type', text_element.type_attr)

      comment_text.text = text_element.content

    #title
    if(comment.title_element):
      comment_title = ET.SubElement(comment_element, 'title')
      comment_title.text = comment.title_element

    #note
    for note_element in comment.note_elements:
      comment_note = ET.SubElement(comment_element, 'note')
      if(note_element.type_attr):
        comment_note.set('type', note_element.type_attr)

      comment_note.text = note_element.content

    #instructions
    for instructions_element in comment.instructions_elements:
      comment_instructions = ET.SubElement(comment_element, 'instructions')
      if(instructions_element.type_attr):
        comment_instructions.set('type', instructions_element.type_attr)

      comment_instructions.text = instructions_element.content

    #response
    for response_element in comment.response_elements:
      comment_response = ET.SubElement(comment_element, 'response')
      if(response_element.type_attr):
        comment_response.set('type', response_element.type_attr)
      #response->text
      for text_element in response_element.text_elements:
        response_text = ET.SubElement(comment_response, 'text')
        if(text_element.type_attr):
          response_text.set('type', text_element.type_attr)

        response_text.text = text_element.content

      #response->validation
      for validation_element in response_element.validation_elements:
        response_validation = ET.SubElement(comment_response, 'validation')
        if(validation_element.type_attr):
          response_validation.set('type', validation_element.type_attr)

        for validation_key in validation_element.content.iterkeys():
          response_validation_element = ET.SubElement(response_validation, validation_key)
          response_validation_element.text = validation_element.content[validation_key]

      #response->bnf
      for bnf_mapping_element in response_element.bnf_mapping_elements:
        response_bnf_mapping = ET.SubElement(comment_response, 'BNF_mapping')
        response_bnf_mapping.set('id', bnf_mapping_element.id_attr)
        if(bnf_mapping_element.type_attr):
          response_bnf_mapping.set('type', bnf_mapping_element.type_attr)

        if(bnf_mapping_element.when_attr):
          response_bnf_mapping.set('when', bnf_mapping_element.when_attr)

        response_bnf_mapping.text = bnf_mapping_element.content

      #response->note
      for note_element in response_element.note_elements:
        response_note = ET.SubElement(comment_response, 'note')
        if(note_element.type_attr):
          response_note.set('type', note_element.type_attr)

        response_note.text = note_element.content

      #response->option
      for option_element in response_element.option_elements:
        response_option = ET.SubElement(comment_response, 'option')
        response_option.set('id', option_element.id_attr)
        if(option_element.clone_attr):
          response_option.set('clone', option_element.clone_attr)

        #response->option->text
        if(option_element.text_element):
          response_option_text = ET.SubElement(response_option, 'text')
          if(option_element.text_element.type_attr):
            response_option_text.set('type', option_element.text_element.type_attr)

          try:
            response_option_text.text = option_element.text_element.content
          except ValueError:
            print option_element.text_element.content
            raise

        #response->option->bnf
        if(option_element.bnf_mapping_elements):
          for bnf_mapping_element in option_element.bnf_mapping_elements:
            response_option_bnf_mapping = ET.SubElement(response_option, 'BNF_mapping')
            response_option_bnf_mapping.set('id', bnf_mapping_element.id_attr)
            if(bnf_mapping_element.type_attr):
              response_option_bnf_mapping.set('type', bnf_mapping_element.type_attr)

            if(bnf_mapping_element.when_attr):
              response_option_bnf_mapping.set('when', bnf_mapping_element.when_attr)

            response_option_bnf_mapping.text = bnf_mapping_element.content

        #response->option->note
        if(option_element.note_element):
          response_option_note = ET.SubElement(response_option, 'note')
          if(option_element.note_element.type_attr):
            response_option_note.set('type', option_element.note_element.type_attr)

          response_option_note.text = option_element.note_element.content

        #response->option->validation
        if(option_element.validation_element):
          response_option_validation = ET.SubElement(response_option, 'validation')
          if(option_element.validation_element.type_attr):
            response_option_validation.set('type', option_element.validation_element.type_attr)

          for validation_key in option_element.validation_element.content.iterkeys():
            response_option_validation_element = ET.SubElement(response_option_validation, validation_key)
            response_option_validation_element.text = option_element.validation_element.content[validation_key]
  #Index->groups
  for group in elements.__groups__:
    populate_group(group, INDEX)

def write(output_file):
  """Receives a path and writes the XML file to it"""

  #tree = ET.ElementTree(ROOT)
  f = open(output_file, 'w')
  f.write(ET.tostring(ROOT, pretty_print=True))
  f.close()

def populate_group(group, GROUP_PARENT):
  """Receives a group object and a XML element and populates this element
  with the group object"""
  group_element = ET.SubElement(GROUP_PARENT, 'group')
  group_element.set('level', str(group.level_attr))
  if(group.title_attr):
    group_element.set('title', group.title_attr)

  if(group.comment_ref_attr):
    group_element.set('comment_ref', group.comment_ref_attr)

  if(group.next_attr):
    group_element.set('next', group.next_attr )

  if(group.back_attr):
    group_element.set('back', group.back_attr)

  #groups->instructions
  for instructions_element in group.instructions_elements:
    group_instructions = ET.SubElement(group_element, 'instructions')
    if(instructions_element.type_attr):
      group_instructions.set('type', instructions_element.type_attr)

    group_instructions.text = instructions_element.content

  #groups->text
  for text_element in group.text_elements:
    group_text = ET.SubElement(group_element, 'text')
    if(text_element.type_attr):
      group_text.set('type', text_element.type_attr)

    group_text.text = text_element.content

  #groups->page
  for page_element in group.page_elements:
    group_page = ET.SubElement(group_element, 'page')
    if(page_element.title_attr):
      group_page.set('title', page_element.title_attr)

    if(page_element.comment_ref_attr):
      group_page.set('comment_ref', page_element.comment_ref_attr)

    #groups->page->instructions
    for instructions_element in page_element.instructions_elements:
      page_instructions = ET.SubElement(group_page, 'instructions')
      if(instructions_element.type_attr):
        page_instructions.set('type', instructions_element.type_attr)

      page_instructions.text = instructions_element.content

    #groups->page->text
    for text_element in page_element.text_elements:
      page_text = ET.SubElement(group_page, 'text')
      if(text_element.type_attr):
        page_text.set('type', text_element.type_attr)

      page_text.text = text_element.content

    #groups->page->includes
    for include_element in page_element.include_elements:
      page_include = ET.SubElement(group_page, 'include')
      page_include.set('qref', include_element.qref_attr)

  #groups-groups
  for group_child in group.group_elements:
    populate_group(group_child, group_element)

