"""Module to create objects for the elements Classes based in a specific plain
text format. More information in utils/docx_format.txt"""

import re
import json
from papofeed import elements, extractor

QUESTION_ID_PREFIX = 'q.'
TYPE_ATTR_JSON = 'json'
#[MEMO] or [TEXTBOX] or [NUMERICAL] or [INSERT] or [|(.*|)+] or [:(.*:)+]
PLAIN_TEXT_TAGS_REGEX = '((\[MEMO\]|\[TEXTBOX\]|\[NUMERICAL\]|\[\|(.*\|)+\]|\[:(.*:)+\]|\[INSERT\])(?:\{([^}]*)\})?)'

#line = current line
#id attribute
def replace_with_json(line, id_attr=''):
  """For each line of the plain text string, replaces the SPECIAL FIELDS with
  JSON code described in utils/questionnaire_tag_description.docx"""

  embedded_json_letter = 'a'
  match = re.search(PLAIN_TEXT_TAGS_REGEX, line) #A match object
  def json_validation():
    validation = {} #a dictionary
    if(match.group(5)):
      validation_pairs = match.group(5).split(";;") #delinieated using ;
      for validation_pair in validation_pairs:
        validation_pair = validation_pair.split("::") #delinieated using :
        validation[re.sub('^( )+|( )+$', '', validation_pair[0])] = re.sub('^( )+|( )+$', '', validation_pair[1])
    return validation

  while(match):#while the match object is found
    embedded_json = {}
    cloze = {}
    cloze['id'] = id_attr + '.' + embedded_json_letter
    embedded_json['cloze'] = cloze
    if(match.group(2) == '[MEMO]'):
      validation = json_validation()
      cloze['type'] = 'memo'
      if(validation):
        if(validation.has_key('default')):
          cloze['default'] = validation.pop('default')

        if(validation):
          cloze['validation'] = validation

      line = re.sub('\[MEMO\](\{([^}]*)\})?', json.dumps(embedded_json), line, 1)

    if(match.group(2) == '[TEXTBOX]'):
      validation = json_validation()
      cloze['type'] = 'textbox'
      if(validation):
        if(validation.has_key('default')):
          cloze['default'] = validation.pop('default')

        if(validation):
          cloze['validation'] = validation

      line = re.sub('\[TEXTBOX\](\{([^}]*)\})?', json.dumps(embedded_json), line, 1)

    if(match.group(2) == '[NUMERICAL]'):
      validation = json_validation()

      cloze['type'] = 'numerical'
      if(validation):
        if(validation.has_key('default')):
          cloze['default'] = validation.pop('default')

        if(validation):
          cloze['validation'] = validation

      line = re.sub('\[NUMERICAL\](\{([^}]*)\})?', json.dumps(embedded_json), line, 1)

    if(re.search('\[\|(.*\|)+\]', match.group(1))):
      validation = json_validation()
      cloze['type'] = 'select one'
      options = match.group(3).split('|')
      options.pop() #removes last '|'
      cloze['options'] = options
      if(validation):
        if(validation.has_key('default')):
          cloze['default'] = validation.pop('default')

        if(validation):
          cloze['validation'] = validation

      line = re.sub('\[\|(.*\|)+\](\{([^}]*)\})?', json.dumps(embedded_json), line, 1)

    if(re.search('\[:(.*:)+\]', match.group(1))):
      validation = json_validation()
      cloze['type'] = 'select multi'
      options = match.group(4).split(':')
      options.pop() #removes last ':'
      cloze['options'] = options
      if(validation):
        if(validation.has_key('default')):
          cloze['default'] = validation.pop('default')

        if(validation):
          cloze['validation'] = validation

      line = re.sub('\[:(.*:)+\](\{([^}]*)\})?', json.dumps(embedded_json), line, 1)

    if(match.group(2) == '[INSERT]'):
      embedded_json = {}
      insert = {}
      mod = {}
      insert_attributes = ['cref','qref','math','count','separator']
      validation = json_validation() #stores the qref
      if(validation): #if the qref exists
        for key in validation.iterkeys():
          if(key in insert_attributes):
			if(key == 'separator'):
			  newKey = validation[key]
			  newKey = newKey[1:-1]
			  validation[key] = newKey
			  insert[key] = validation[key]
			else:
			  insert[key] = validation[key]
          else:
            mod[key] = validation[key]
        if(mod):
          insert['mod'] = mod
      else:
        #TODO
        raise Exception ("TO DO, check feed.py line 124")
      embedded_json['insert'] = insert
      line = re.sub('\[INSERT\](\{([^}]*)\})?', json.dumps(embedded_json), line, 1)

    embedded_json_letter = chr(ord(embedded_json_letter) + 1)
    match = re.search(PLAIN_TEXT_TAGS_REGEX, line)

  return line

"""
parse(plain_text)
Handles reading text file contents and creating/storing relevant tree elements.
"""
def parse(plain_text):
  
  """find_nth(haystack, needle, n)
  Input: haystack(the string), needle(item to look for), (the occurance # to look for)
  Output: Integer position
  Functionality: returns the index(start) of the nth occurrence of character needle in string haystack """
  def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start
  
  """
  replaceRegCatDelinForMod
  Convert :: delins in regular Category Mod statements to : delineators
  """
  def replaceRegCatDelinForMod(convertedRegularCategoryArray):
	index = 0
	for regCatSyntax in convertedRegularCategoryArray: #insertSyntax is a Str
		#convert to list, replace :: with :, then convert back to string
		regCatString = regCatSyntax.replace("::", ":")
		convertedRegularCategoryArray[index] = regCatString
		index = index + 1

	return convertedRegularCategoryArray
  
  """convertRegCatToXML
  Input: Array of stripped raw categories
  Output: Array of regular categories with the values in the input array held in double quotes
  Functionality: Converts each item in the input array into a list, inserts double quotes at the end and beginning of the qref value,
  turns it back into a string, and adds it to an array of converted regular category that it then returns.
  """
  def convertRegCatToXML(convertedRegularCategoryArray):

	counter = 0
	convertedRegularCategoryArray = replaceRegCatDelinForMod(convertedRegularCategoryArray)
	
	while(counter < len(convertedRegularCategoryArray)):
	  rawText = list(convertedRegularCategoryArray[counter])
	  rawText.insert(0,'"')
	  rawText.insert(rawText.index(':'), '"')
	  convertedCategoryText = ''.join(rawText)

	  convertedRegularCategoryArray[counter] = convertedCategoryText
	  counter += 1

	return convertedRegularCategoryArray

  """
  replaceDelineatorsForMod
  Convert :: delins in mod statements to : delineators
  """
  def replaceInsertDelinForMod(convertedInsertArray):
	index = 0
	for insertSyntax in convertedInsertArray: #insertSyntax is a Str
		#convert to list, replace :: with :, then convert back to string
		insertString = insertSyntax.replace("::", ":")
		insertString = insertString.replace(";;", ",")
		convertedInsertArray[index] = insertString
		index = index + 1
	return convertedInsertArray
  
  """
  Input: Array of stripped insert categories
  Output: Array of insert categories with the values in the input array held in double quotes
  Functionality: Accounting for insert postions - beginning of a insert(mod(insert)), middle of a insert(mod(insert)), or a regular category in a insert(mod(insert))
  Strip of relevant syntax, and convert to a regular delineated pair.
  """
  def convertInsertArrayToXML(convertedInsertArray):
	counter = 0
	convertedInsertArray = replaceInsertDelinForMod(convertedInsertArray)
	while (counter < len(convertedInsertArray)):
	  rawText = convertedInsertArray[counter]
	  
	  #beginning inserts
	  if(rawText.startswith("StartIns")):
		rawText = rawText.replace("StartIns[INSERT]{","{\"insert\": {")
		separator = ""
		if(rawText.find("separator:\"") != -1):
		  separatorText = rawText[rawText.find("separator:\""):]
		  separator = separatorText[find_nth(separatorText, "\"", 1)+1:find_nth(separatorText, "\"", 2)]
		listText = rawText[rawText.find("qref"):-1]
		
		#to account for commas used for separators and other issues that may arise with some insert attributes
		#need to split string up by attribute pattern, not by commas.
		insertAttributeIndexes = [(m.start(0)) for m in re.finditer(",\w\w\w\w",listText) ]
		insertAttributeIndexes.insert(0,0)
		parts = [listText[i:j] for i,j in zip(insertAttributeIndexes, insertAttributeIndexes[1:]+[None])]
		
		#now that it's split by the start index of each pair
		#need to get rid of the comma in front of each attribute start
		count = 0
		while count < len(parts):
		  part = parts[count]
		  if part[0] == ",":
		    part = part[1:]
		    parts[count] = part
		  count = count + 1
	
		listPairs = parts
		moddedListPairs = []
		numPairs = len(listPairs)
		rawText = rawText[:-1] + ","
		
		#go through the pairs
		#if a pair still has a delineator surrounded by slashes, remove the slashes, add double quotes around the attribute and then add it to moddedListPairs
		#otherwise just add it to moddedListPairs with double quotes added.
		a = 0
		while(a < numPairs):
		  if(listPairs[a].find("\""+separator+"\"") == -1):
			moddedListPairs.append("\"" + listPairs[a][:listPairs[a].find(":")] + "\"" + listPairs[a][listPairs[a].find(":"):listPairs[a].find(":")+1] + "\"" + listPairs[a][listPairs[a].find(":")+1:] + "\"")
		  else:
			moddedListPairs.append("\"" + listPairs[a][:listPairs[a].find(":")] + "\"" + listPairs[a][listPairs[a].find(":"):])
		  
		  rawText = rawText.replace(listPairs[a], moddedListPairs[a])
		  a = a + 1
		convertedInsertArray[counter] = rawText

	  #inserts enclosed within mods
	  elif(rawText.startswith("middleMod")):
		rawText = rawText[rawText.find("[INSERT]"):]
		rawText = rawText.replace("[INSERT]", "{~~$insert~~$:") #insert changes
		rawText = rawText + "}" #ending brace
		separator = ""
		if(rawText.find("separator:\"") != -1):
		  separatorText = rawText[rawText.find("separator:\""):]
		  separator = separatorText[find_nth(separatorText, "\"", 1)+1:find_nth(separatorText, "\"", 2)]
		  rawText = rawText.replace("\"" + separator + "\"", "~~$"+separator+"~~$")
		listText = rawText[rawText.find("qref"):-2]
		#to account for commas used for separators and other issues that may arise with some insert attributes
		#need to split string up by attribute pattern, not by commas.
		insertAttributeIndexes = [(m.start(0)) for m in re.finditer(",\w\w\w\w",listText) ]
		insertAttributeIndexes.insert(0,0)
		parts = [listText[i:j] for i,j in zip(insertAttributeIndexes, insertAttributeIndexes[1:]+[None])]
		#now that it's split by the start index of each pair, need to get rid of the comma in front of each attribute start
		count = 0
		while count < len(parts):
		  part = parts[count]
		  if part[0] == ",":
		    part = part[1:]
		    parts[count] = part
		  count = count + 1
		
		listPairs = parts

		moddedListPairs = []
		numPairs = len(listPairs)
		
		#go through the pairs
		#if a pair still has a delineator surrounded by slashes, remove the slashes, add double quotes around the attribute and then add it to moddedListPairs
		#otherwise just add it to moddedListPairs with double quotes added.
		a = 0
		while(a < numPairs):
		  if(listPairs[a].find("~~$"+separator+"~~$") == -1):
			moddedListPairs.append("~~$" + listPairs[a][:listPairs[a].find(":")] + "~~$" + listPairs[a][listPairs[a].find(":"):listPairs[a].find(":")+1] + "~~$" + listPairs[a][listPairs[a].find(":")+1:] + "~~$")
		  else:
			moddedListPairs.append("~~$" + listPairs[a][:listPairs[a].find(":")] + "~~$" + listPairs[a][listPairs[a].find(":"):])
		  
		  rawText = rawText.replace(listPairs[a], moddedListPairs[a])
		  a = a + 1
		
		convertedInsertArray[counter] = rawText
		
	  #regular categories within insert(mod(inserts), reg cat, reg cat, reg cat)
	  elif(rawText.startswith("Reg")):

		rawText = rawText[rawText.find("[INSERT]"):]
		rawText = rawText.replace("[INSERT]", "{\"insert\":") #insert changes
		separator = ""
		if(rawText.find("separator:\"") != -1):
		  separatorText = rawText[rawText.find("separator:\""):]
		  separator = separatorText[find_nth(separatorText, "\"", 1)+1:find_nth(separatorText, "\"", 2)]
		
		listText = rawText[rawText.find("qref"):-1]

		#to account for commas used for separators and other issues that may arise with some insert attributes
		#need to split string up by attribute pattern, not by commas.
		insertAttributeIndexes = [(m.start(0)) for m in re.finditer(",\w\w\w\w",listText) ]
		insertAttributeIndexes.insert(0,0)
		parts = [listText[i:j] for i,j in zip(insertAttributeIndexes, insertAttributeIndexes[1:]+[None])]

		#now that it's split by the start index of each pair, need to get rid of the comma in front of each attribute start
		count = 0
		while count < len(parts):
		  part = parts[count]
		  if part[0] == ",":
		    part = part[1:]
		    parts[count] = part
		  count = count + 1
	
		listPairs = parts
		moddedListPairs = []
		numPairs = len(listPairs)

		#go through the pairs
		#if a pair still has a delineator surrounded by slashes, remove the slashes, add double quotes around the attribute and then add it to moddedListPairs
		#otherwise just add it to moddedListPairs with double quotes added.
		a = 0
		while(a < numPairs):
		  if(listPairs[a].find("\""+separator+"\"") == -1):
			moddedListPairs.append("\"" + listPairs[a][:listPairs[a].find(":")] + "\"" + listPairs[a][listPairs[a].find(":"):listPairs[a].find(":")+1] + "\"" + listPairs[a][listPairs[a].find(":")+1:] + "\"")
		  else:
			moddedListPairs.append("\"" + listPairs[a][:listPairs[a].find(":")] + "\"" + listPairs[a][listPairs[a].find(":"):])
		  rawText = rawText.replace(listPairs[a], moddedListPairs[a])
		  a = a + 1
		convertedInsertArray[counter] = rawText + "}"

	  else:
	    raise Exception("Uh oh, there's something wrong with the insert formatting. Check convertedInsertArray")
	  counter = counter + 1

	return convertedInsertArray
	
  """replaceArrayWithXML
  Replaces the full line XML's unconverted regular category strings with the converted regular category strings
  """
  def replaceArrayWithXML(fullStatement, originalStrings, convertedStrings):

    arrayPos = 0
    while(arrayPos < len(originalStrings)):#loop through the line
	  originalString = originalStrings[arrayPos]
	  convertedString = convertedStrings[arrayPos]
	  
	  #in cases where the full statement and the two strings differ because of a removed inner insert
	  if originalString.endswith("\""):
	    if originalString[-2:-1] == " ": #second to last char
		  originalString = originalString[:-1]
		  convertedString = convertedString[:-1]
	  
	  #same, but at the end of the mod statement
	  if originalString.endswith("\"}"):
		if originalString[-3:-2] == " ":
		  originalString = originalString[:-2]
		  convertedString = convertedString[:-4]
	  
	  if(originalString in fullStatement):#check to see if the reg category is in the original line. Replace the first instance
		fullStatement = fullStatement.replace(originalString, convertedString, 1)
	  arrayPos += 1 

    return fullStatement
  
  """cleanupFinalStatement(String fullStatement)
  Input: the converted line with a few errors still remaining
  Output: the final string, ready for writing"""
  def cleanupFinalStatement(fullStatement): 
	#Gets rid of [ in mods and adds a ' {' to ending mod inserts.
	#add 2 ending brackets to a mod - find the index of a mod, then the index of the 3rd ending bracket.
	#find index of mod - make string from mod start to end.
	fullStatement = re.sub("\[MOD\]", "\"mod\":", fullStatement)
	modInsertPos = []
	
	#find all mod inserts
	for modIndex in list(re.finditer("{'insert'", fullStatement)):
	  modInsertPos.append(modIndex.start())

	#now get delete everything up to and including the nearest "
	counter = 0
	while(counter < len(modInsertPos)):
	  tempString = fullStatement[:modInsertPos[counter]]
	  if(tempString[len(tempString)-1:len(tempString)] == "{"):
	    raise Exception("There is an error with your MOD statement. MOD statements cannot have an INSERT statement as the first thing in their contents. This creates a parsing error with JINJA2. Currently, MOD statements must start with a qrefContents::Text pair. ")
	  deleteTo = tempString.rfind("\"")
	  deleteToContentsLen = modInsertPos[counter] - deleteTo
	  
	  fullStatement = fullStatement[:deleteTo] + fullStatement[deleteTo+deleteToContentsLen:]
	  
	  #counteracts modInsertPos value being wrong after changing fullStatement
	  if(counter+1 < len(modInsertPos)): 
	    modInsertPos[counter+1] = modInsertPos[counter+1] - deleteToContentsLen
	  counter += 1

	  
	#mods that have a insert at the end need an extra }} appended at the very end.
	#look for "}"} "
	#get index of match, add }}
	endModInsertPos = fullStatement.find("}\"}")
	if(endModInsertPos != -1):
	  fullStatement = fullStatement[:endModInsertPos+2] + "}}" + fullStatement[endModInsertPos+2:]
	#add }} if fullstatement ends with incomplete mod statement
	if fullStatement.endswith("\"}"):
	  fullStatement = fullStatement + "}}"
	
	#add }} to mod statement if it's incomplete, but not at the end of the statement
	#cases in which there are "} and next char is not }
	#add }}
	#DO NOT LOSE THE CHAR DIRECTLY AFTER THE "}
	listCharAfterModInserts = [m.end(0) for m in re.finditer("\"}[^}]", fullStatement)]
	listChars = []
	counter = 0
	while counter < len(listCharAfterModInserts):
	  listChars.append(fullStatement[listCharAfterModInserts[counter]-1])
	  counter = counter + 1
	fullStatement = re.sub(("\"}[^}]"),("\"}}}"), fullStatement)
	
	#reverse the listCharAfterModInserts and listChars
	listCharAfterModInserts.reverse()

	#loop through listCharAfterModInserts, get the ending indexes (but in reverse so that adding chars won't effect the other indexes)
	#add length of listCharAfterModInserts to the index
	#using counter, get item in list char
	#take the fullStatement and add item in list char @ index of match + length of listCharAfterModInserts
	counter = 0
	listCharsIterator = len(listChars)#use this to make the character immediately following a mod fall into the right index
	while counter < len(listCharAfterModInserts):
		matchIndex = listCharAfterModInserts[counter]
		missingChar = listChars[counter]
		additionAfterSubbing = len(listCharAfterModInserts)
		fullStatement = fullStatement[:matchIndex+listCharsIterator] + missingChar + fullStatement[matchIndex+listCharsIterator:]
		counter = counter + 1
		listCharsIterator = listCharsIterator - 1
	
	fullStatement = re.sub(("~~\$\s*"),("~~$"), fullStatement)
	fullStatement = re.sub(("\s*~~\$"),("~~$"),fullStatement)
	fullStatement = re.sub(("{\s*\"qref\""),("{\"qref\""),fullStatement)
	fullStatement = re.sub(("\"mod\":{\s*"),("\"mod\":{"),fullStatement)
	
	#to allow double quotes within double quotes in mod, we use the \" escape sequence
	#but this messes up the previous qref and the :: to : conversion
	#need to manually sub in the correct fixes to the errors
	fullStatement = re.sub(("::"),("\":"), fullStatement)
	fullStatement = re.sub(("{q"),("{\"q"), fullStatement)
	fullStatement = re.sub((" q"),(" \"q"), fullStatement)

	return fullStatement

  """linePreProcessing(string line)
  need to get rid of whitespace after :: sequences in the mod statement line
  """
  def linePreProcessing(line):
	#find all of the matches
	
	pairMatches = re.findall("\w*::\s*\"", line)
	numMatches = len(pairMatches) #finds # of MOD qref/label pairs.
	changedMatches = []
	
	#iterate through matches
	for match in pairMatches:
	  changedMatches.append(re.sub(" ","", match))
	
	#then loop through all matches again, and sub in the changed ones using re.sub
	counter = 0
	while counter < numMatches:
	  line = re.sub(pairMatches[counter], changedMatches[counter], line)
	  counter = counter + 1
	
	#[MOD] flexibility
	#search the line for spaces between and after [MOD] and get rid of them.
	line = re.sub("\s*\[MOD\]","[MOD]",line)
	line = re.sub("\[MOD\]\s*","[MOD]",line)
	line = re.sub("\s*\[MOD\]\s*","[MOD]",line)
	
	line = re.sub(("\s*::"),("::"),line)
	return line
  
  """removeInsertWS
  Get rid of white space after the :: and ;; delineators, as well as need to get rid of white-spaces between the end of an insert and non-white-space character. 
  """
  def removeInsertWS(line):
	#Find all the inserts + 3 characters afterwards.
	#If any are spaces or tabs, sub with ""
	linePosition = 0
	lineLength = len(line)
	originalInsertList = []
	while (linePosition < lineLength):
	  if (linePosition + 2 < lineLength):
	    firstChar = line[linePosition]
	    secondChar = line[linePosition+1]
	    thirdChar = line[linePosition+2]
	    checkInsertSequence = firstChar + secondChar + thirdChar
	    if(checkInsertSequence == '[IN'): #Once we find an insert 	 
		  placeholderString = line[linePosition:] #placeholder string holds the start of an index to the end of the array
		  startOfInsertString = placeholderString[:placeholderString.index('}')+3]#The entire insert
		  originalInsertList.append(startOfInsertString)
	  linePosition += 1

	counter = 0
	modifiedInsertList = []
	while(counter < len(originalInsertList)):
	  newInsert = originalInsertList[counter]
	  #if whitespace is detected directly before or after ';;', remove it.
	  newInsert = re.sub(";;\s*", ";;",newInsert)
	  newInsert = re.sub("\s*;;", ";;",newInsert)
	  #if whitespace is detected directly before or after '::', remove it.
	  newInsert = re.sub("::\s*", "::", newInsert)
	  newInsert = re.sub("\s*::", "::", newInsert)
	  #if whitespace is detected before a closing bracket, remove it
	  newInsert = re.sub("\s*}", "}", newInsert)
	  modifiedInsertList.append(newInsert)
	  line = line.replace(originalInsertList[counter], modifiedInsertList[counter])
	  counter +=1

	return line
  
  """
  Gigantic (probably way too big and needs to be split up) function that handles all XML conversion for MOD and INSERT statements.
  Returns a successfully converted MOD and/or INSERT statement.
  """
  def convertToXML(line, mod):
	
	line = linePreProcessing(line)
	lineLength = len(line)
	fullStatement = line

	insertArray = []
	convertedInsertArray = []
	modArray = []
	convertedModArray = []
	regularCategoryArray = []
	convertedRegularCategoryArray = []
	modStringForSkipping = ""
	
	linePosition = 0

	"""Mod stuff, including the inserts in Mod"""
	#Look for MOD or REGULAR CATEGORY. First step: search the line for the mod segment location
	while (linePosition < lineLength):
	  if (linePosition + 3 < lineLength):
	    colonChar1 = line[linePosition]
	    colonChar2 = line[linePosition+1]
	    dQuoteChar = line[linePosition+2] #these hold three characters as the loop goes through the string
	    insertSeperatorChar = line[linePosition+3]
	    checkModSequence = colonChar1 + colonChar2 + dQuoteChar
	    checkIfInsertSeperator = colonChar1 + colonChar2 + dQuoteChar + insertSeperatorChar
	    if(checkModSequence == '::"' and checkIfInsertSeperator != '::",'): #once it finds the specific 3 character sequence

		  modOrRegularString = line[line.find("[MOD]"):] #so now  we have the mod string to the end, starting at the first {
		  #handle whitespace issues for mod endings
		  #replace \ } and } } with nonwhitespace versions
		  modOrRegularString = re.sub("\"\s}","\"}", modOrRegularString)
		  modOrRegularString = re.sub("}\s}","}}", modOrRegularString)
		  modPositions = [m.start() for m in re.finditer("[\w\W]\"}", modOrRegularString)] #for multiple mods in a single line. Means you can't have "} or }}. Searches for alphanumeric+"+}
		  #loop through mod Positions
		  modCount = 0
		  
		  while modCount < len(modPositions):
			regularCategoryArray = []
			convertedRegularCategoryArray = []
			singleModOrRegularString = modOrRegularString
			dqB = modPositions[modCount]
			bB = modOrRegularString.rfind("}}") #This could result in a bug later for multiple mods in one line that both end with the middle insert. Fix in future.
			if(dqB > -1 and bB > -1):
				posList = [dqB, bB]
				endModIndex = min(posList)
			elif(dqB == -1 and bB == -1):
				raise Exception("Mod Syntax is incorrect")
			else: 
				if(dqB > bB):
					endModIndex = dqB
				elif(bB > dqB):
					endModIndex = bB
				else:
					raise Exception("Uh oh, bug in the code.")
		    

			singleModOrRegularString = singleModOrRegularString[:endModIndex+3]#the full mod statement! +3 is to accommodate for \w"}
			singleModOrRegularString = singleModOrRegularString[singleModOrRegularString.rfind("[MOD]"):]
			modStringForSkipping = singleModOrRegularString #we use this later to skip over the rest of the mod statement within the text parsing loop.
			
		    #get rid of inserts so that we can detect the ends of the regular categories using ", and endModIndex value for the last one
			numInserts = singleModOrRegularString.count("[INSERT]")
			while(numInserts):
				insertIndex = singleModOrRegularString.find("[INSERT]")
				tempString = singleModOrRegularString[insertIndex:]
				endInsertIndex = tempString.find("}")
				insertString = singleModOrRegularString[insertIndex:insertIndex+endInsertIndex+1] #the entire insert chunk

				#find the pos of the insertString in line
				relativeInsertPos = line.find(insertString)
			
				#substring beginning to relative insert pos
				checkModString = line[:relativeInsertPos]

				#find the nearest [MOD]
				#if none, then skip
				modExists = checkModString.find("MOD")
			
				#if there is one, then substring the line from the nearest mod to the current insert
				#count the number of { and }, if { is greater, then signifies that the insert is within a MOD
				#Need to do it this way to avoid complications with regular inserts that occur after a MOD statement is completed.
				lBracketCount = 0
				rBracketCount = 0
				if(modExists != -1):
					tempString = checkModString[modExists:]
					lBracketCount = tempString.count('{')
					rBracketCount = tempString.count('}')
					if(lBracketCount > rBracketCount):
						insertIndex = singleModOrRegularString.find("[INSERT]")
						tempString = singleModOrRegularString[insertIndex:]
						endInsertIndex = tempString.find("}")
						insertString = singleModOrRegularString[insertIndex:insertIndex+endInsertIndex+1] #the entire insert chunk

						#now do the modifying and saving business.
						insertArray.append(insertString)
						markedInsertString = "middleMod" + insertString
						convertedInsertArray.append(markedInsertString)
			
						#also remove it from the line
						#find position of index in mod string
						insertIndexInMod = singleModOrRegularString.find(insertString)
						modIndexInLine = line.find(singleModOrRegularString)
						#find position of modstring in line
						#remove insert by substringing line[:modstart+insertstart] + line[modstart+insertstart+insertlength:]
						line = line[:modIndexInLine+insertIndexInMod] + line[modIndexInLine+insertIndexInMod+len(insertString):]
						lineLength = len(line)

						#then remove it from singleModOrRegularString
						singleModOrRegularString = singleModOrRegularString[:insertIndexInMod] + singleModOrRegularString[insertIndexInMod + len(insertString):]
	
				numInserts = numInserts - 1

			singleModOrRegularString = re.sub("\"\s,", "\",", singleModOrRegularString) #to make sure ", exist. May be " , otherwise.

			regCatCount = len(re.findall("::\"\w", singleModOrRegularString))
			regCatIndexes = [(m.start()) for m in re.finditer("::\"\w", singleModOrRegularString)]
		    #now that we have the number of regular category mods, then we
			#extract the regular categories. Ex. q.1.7.d.a::"option C". Include the } for the last one.
			#add the string to both regularCategoryArray and convertedCategoryArray
			count = 0
			test1 = []

			while (count < regCatCount):
				regCatIndex = regCatIndexes[count]
				singleModOrRegularString = re.sub(",\s*", ",", singleModOrRegularString)
				singleModOrRegularString = re.sub("\[MOD\]{\s*", "[MOD]{", singleModOrRegularString)
				
				regCatEndLengthString = singleModOrRegularString[regCatIndex:]
				regCatEndLength1 = regCatEndLengthString.find("\",") #means no ", in the mod value
				regCatEndLength2 = regCatEndLengthString.find("\"}") #means no "} in the mod value
				regCatEndLength = 0
				secondHalf = ""
				secondHalfMarker = ""
				if(regCatEndLength1 != -1): #if a beginning or middle category
				  secondHalf = singleModOrRegularString[regCatIndex:regCatIndex+regCatEndLength1+1]#regCatEndLength = regCatEndLength1+1
				  
				  regCatStartLengthString = singleModOrRegularString[:regCatIndex]
				  regCatStartLength1 = regCatStartLengthString.rfind("[MOD]{")
				  regCatStartLength2 = regCatStartLengthString.rfind("\",")
				  if(regCatStartLength1 > regCatStartLength2):
				    firstHalf = regCatStartLengthString[regCatStartLength1+6:] 
				  else:
				    firstHalf = regCatStartLengthString[regCatStartLength2+2:]
				  
				  regCatString = firstHalf+secondHalf
				  regCatString = re.sub("\s*::","::",regCatString)

				  regularCategoryArray.append(regCatString)
				  convertedRegularCategoryArray.append(regCatString)
				  
				elif(regCatEndLength2 != -1): #if the ending category
				  secondHalf = singleModOrRegularString[regCatIndex:regCatIndex+regCatEndLength2+2]#regCatEndLength = regCatEndLength2+2  #2 is so that we include the ending bracket
				  secondHalfMarker = singleModOrRegularString[regCatIndex:regCatIndex+regCatEndLength2+2]
				  
				  regCatStartLengthString = singleModOrRegularString[:regCatIndex]
				  regCatStartLengthString = re.sub("\s*:",":",regCatStartLengthString)
				  regCatStartLength1 = regCatStartLengthString.rfind("[MOD]{") #means no [MOD]{ allowed in the mod key
				  regCatStartLength2 = regCatStartLengthString.rfind("\",") #means no ", allowed in the mod key
				  if(regCatStartLength1 > regCatStartLength2):
				    firstHalf = regCatStartLengthString[regCatStartLength1+6:] 
				  else:
				    firstHalf = regCatStartLengthString[regCatStartLength2+2:]
				  
				  regCatString = firstHalf+secondHalf
				  regCatString = re.sub("\s*::","::",regCatString)
				  
				  regCatStringMarker = firstHalf + secondHalfMarker
				  regCatStringMarker = re.sub("\s*::","::",regCatStringMarker)

				  regularCategoryArray.append(regCatString)
				  convertedRegularCategoryArray.append(regCatStringMarker)
				else: raise Exception("Re-check Mod Syntax for odd regular category formatting")
				
				count = count + 1

			#Loop through regularCategoryArray, look for matches in fullStatement(the line), delete it, and replace each match with the corresponding counter in convertedRegularCategoryArray
			convertedRegularCategoryArray = convertRegCatToXML(convertedRegularCategoryArray)
			fullStatement = replaceArrayWithXML(fullStatement, regularCategoryArray, convertedRegularCategoryArray)
			modCount = modCount + 1
			
			modLength = len(modStringForSkipping)
			linePosition = linePosition + modLength #So we don't repeat above for all ::" sequences in the mod statement
	  linePosition += 1  

	"""
	Insert stuff, not including inserts in mods
	"""
	
	#Look for INSERT
	#need to mark mod inserts as so because we need to put those in single quotes, not double like the rest
	linePosition = 0
	lineLength = len(line) #need to redo because we just got a line back from removeInsertWS
	while (linePosition < lineLength):
	  if (linePosition + 2 < lineLength):
	    firstChar = line[linePosition]
	    secondChar = line[linePosition+1]
	    thirdChar = line[linePosition+2]
	    checkInsertSequence = firstChar + secondChar + thirdChar
	    if(checkInsertSequence == '[IN'): #Once we find an insert 	 
		  placeholderString = line[linePosition:] #placeholder string holds the start of an index to the end of the array
		  startOfInsertString = placeholderString[:placeholderString.index('}')+1]#The entire insert
		  textAfterInsert = placeholderString[len(startOfInsertString):]
		  if(textAfterInsert[:2] == "[M"):
			insertArray.append(startOfInsertString)
		  else:
			insertArray.append(startOfInsertString)
	  linePosition += 1
	
	line = removeInsertWS(line)#Get rid of white-space immediately after insert statements to prepare line for insert conversion

	#Look for INSERT
	#need to mark mod inserts as so because we need to put those in single quotes, not double like the rest
	linePosition = 0
	lineLength = len(line) #need to redo because we just got a line back from removeInsertWS
	while (linePosition < lineLength):
	  if (linePosition + 2 < lineLength):
	    firstChar = line[linePosition]
	    secondChar = line[linePosition+1]
	    thirdChar = line[linePosition+2]
	    checkInsertSequence = firstChar + secondChar + thirdChar
	    if(checkInsertSequence == '[IN'): #Once we find an insert 	 
		  placeholderString = line[linePosition:] #placeholder string holds the start of an index to the end of the array
		  startOfInsertString = placeholderString[:placeholderString.index('}')+1]#The entire insert
		  textAfterInsert = placeholderString[len(startOfInsertString):]
		  if(textAfterInsert[:2] == "[M"):			
			startOfInsertString = "StartIns" + startOfInsertString
			convertedInsertArray.append(startOfInsertString)
		  else:
			startOfInsertString = "Reg" + startOfInsertString
			convertedInsertArray.append(startOfInsertString)
	  linePosition += 1
	
	#convert insert statements in convertedInsertArray into XML, then replace it in the array
	convertedInsertArray = convertInsertArrayToXML(convertedInsertArray)
	fullStatement = replaceArrayWithXML(fullStatement, insertArray, convertedInsertArray)
	
	fullStatement = cleanupFinalStatement(fullStatement) #currently just replaces [MOD]
	#need stuff here that takes each mod segment and adds }} to the end of it.
	
	return fullStatement
  
  """deleteCDATAContructs(String fullStatement)"""
  def deleteCDATAContructs(fullStatement):
    #delete '<![CDATA[ ' and ' ]]>' 
	CDATAList = list(fullStatement)
	startCDATA = '<![CDATA[ '
	startCDATALength = 10
	endCDATA = ' ]]>'
	endCDATALength = 4
	counter = 0
	
	while(counter < len(CDATAList)-11):
	  startCDATACheck = ''.join(CDATAList[counter:counter+startCDATALength])
	  if(startCDATACheck == '<![CDATA[ '): # if beginning is found, remove it from the list
	    currPos1 = startCDATALength
	    while(currPos1 > 0):
		  CDATAList.pop(counter)
		  currPos1 = currPos1 - 1  
	  
	  counter += 1
    
	counter = 0
	while(counter < len(CDATAList)-5):
	  endCDATACheck = ''.join(CDATAList[counter:counter+endCDATALength])
	  if(endCDATACheck == '</p>'):
	    currPos2 = endCDATALength 
	    while(currPos2 > 0):
		  CDATAList.pop(counter+4)
		  currPos2 = currPos2 - 1
	  counter = counter + 1    
	fullStatement = ''.join(CDATAList)
	return fullStatement  

  """takes in the line, removes any whitespaces before or after [INSERT],[NUMERICAL], or any other input type"""
  def removeInputTypeSpaces(line):
	#numerical
	line = re.sub("\s*\[NUMERICAL\]","[NUMERICAL]",line)
	line = re.sub("\[NUMERICAL\]\s*","[NUMERICAL]",line)
	line = re.sub("\s*\[NUMERICAL\]\s*","[NUMERICAL]",line)
	#memo
	line = re.sub("\s*\[MEMO\]","[MEMO]",line)
	line = re.sub("\[MEMO\]\s*","[MEMO]",line)
	line = re.sub("\s*\[MEMO\]\s*","[MEMO]",line)
	#textbox
	line = re.sub("\s*\[TEXTBOX\]","[TEXTBOX]",line)
	line = re.sub("\[TEXTBOX\]\s*","[TEXTBOX]",line)
	line = re.sub("\s*\[TEXTBOX\]\s*","[TEXTBOX]",line)
	return line
	
  """receives a string and populates the elements module lists"""
  lines = plain_text.split('\n') #creates an array with each box containing one line of the plain text
  current_question = None
  current_response = None
  current_option = None
  current_option_letter = None
  current_group = None
  groups_tree = []
  current_page = None
  line_index = 0
  bnf_id = 1
  comment_id = 1
  #debug info
  line_dbg = 0
  for line in lines: #goes through the array of lines
	#debug info
    line_dbg += 1 #adds line to the counter (for use in the print console)
    print 'parsing line {0}'.format(line_dbg) #prints the line currently parsing to the console
    # end debug info
    line = removeInputTypeSpaces(line)
    group_match = re.search('^\[GROUP\]\{(\d+)\}: *(.*)', line) #does a regex search for each type of element
    page_match = re.search('^\[PAGE\]: *(.*)', line)
    additional_comments = re.search("^COMMENT: *(.*)", line)
    question_match = re.search('^ID: *((\d+\.)*\d+)', line)
    question_title = re.search('^TITLE: *(.*)', line)
    CDATA_match = re.search('<!\[CDATA\[.*?\]\]>', line) #check for CDATA
    if(CDATA_match):CDATA_match_position = CDATA_match.start() #gets the index CDATA start
    if(CDATA_match):CDATA_match_position_end = 	CDATA_match.end() #gets index of CDATA end
    text_tag = re.search('^TEXT: *(.*)', line)
    response_text_tag = re.search('^RESPONSE_TEXT: *(.*)', line)
    note_tag = re.search('^NOTE: *(.*)', line)
    CDATA_note_tag = re.search('^NOTE: <!\[CDATA\[.*?\]\]>', line)
    instructions_tag = re.search('^INSTRUCTIONS: *(.*)', line)
    response_note_tag = re.search('^RESPONSE_NOTE: *(.*)', line)
    validation_tag = re.search('^VALIDATION: *(?:\{([^}]*)\})?', line)
    response_validation_tag = re.search('^RESPONSE_VALIDATION: *(?:\{([^}]*)\})?', line)
    question_indent = re.search('INDENT: *(.*)', line)
    question_when = re.search('^DISPLAY_WHEN: *(.*)', line)
    question_where = re.search('^DISPLAY_WHERE: *(.*)', line)
    radio_option = re.search('^ *\(\) *(.*)', line)
    select_box_option = re.search('^ *\[\] *(.*)', line)
    option_clone = re.search('^CLONE: *(.*)', line)
    #validations are not included in this regex	
    textbox_response = re.search('^\[TEXTBOX\]$', line)
    memo_response = re.search('^\[MEMO\]$', line)
    cloze_response = re.search('.*(\[MEMO\]|\[TEXTBOX\]|\[NUMERICAL\]|\[\|(.*\|)+\]|\[:(.*:)+\]).*', line)
    insert_response = re.search('.*(\[INSERT\]).*', line)
    bnf_mapping = re.search('^BNF(?: ?\{(.*)\})?: *(.*)', line)
    response_bnf_mapping = re.search('^RESPONSE_BNF(?: ?\{(.*)\})?: *(.*)', line)
    blank_line = re.search('^ *$', line)
    mod = re.search('MOD', line)
    comment_not_to_parse = re.search('^ *#.*', line)

    if(comment_not_to_parse):
      pass
    
    elif(insert_response and mod): 
	  if(note_tag):
	    fullStatement = convertToXML(line, mod)
	    fullStatement = fullStatement[5:] #gets rid of NOTE:
	    if(CDATA_match):
		  fullStatement = deleteCDATAContructs(fullStatement)
	    if(current_option):
		  current_option.note_elements.append(elements.Note(fullStatement,TYPE_ATTR_JSON))
	    elif(current_response):
		  current_response.note_elements.append(elements.Note(fullStatement,TYPE_ATTR_JSON))
	    else:
		  current_question.note_elements.append(elements.Note(fullStatement,TYPE_ATTR_JSON))
	  
	  elif(text_tag):
	    fullStatement = convertToXML(line, mod)
	    fullStatement = fullStatement[5:]
	    if(CDATA_match):
		  fullStatement = deleteCDATAContructs(fullStatement)
	    else:
		  if(current_question):
		    current_question.text_elements.append(elements.Text(replace_with_json(fullStatement)))
		  elif(current_page):
		    current_page.text_elements.append(elements.Text(replace_with_json(fullStatement)))
		  else:
		    current_group.text_elements.append(elements.Text(replace_with_json(fullStatement)))
	  
	  elif(instructions_tag):
		fullStatement = convertToXML(line, mod)
		fullStatement = fullStatement[13:]
		if(CDATA_match):
		  fullStatement = deleteCDATAContructs(fullStatement)
		if(current_question):
		  set_instructions(current_question, fullStatement, insert_response)
		elif(current_page):
		  set_instructions(current_page, fullStatement, insert_response)	
		elif(current_group):
		  set_instructions(current_group, fullStatement, insert_response)
	  
	  elif(bnf_mapping):
	    fullStatement = convertToXML(line,mod)
	    fullStatement = fullStatement[4:]
	    set_bnf2(bnf_mapping, insert_response, bnf_id, current_option, current_response, fullStatement)
	    bnf_id += 1
	  
	  elif(response_bnf_mapping):
	    fullStatement = convertToXML(line, mod)
	    fullStatement = fullStatement[14:]
	    if(CDATA_match):
		  fullStatement = deleteCDATAContructs(fullStatement)
	    bnf_mapping_object = elements.BnfMapping('b.' + str(bnf_id),fullStatement)
	    if(insert_response):
	      bnf_mapping_object.type_attr = TYPE_ATTR_JSON
	      is_response=True
	    if(current_option and (not is_response)):
	      current_option.bnf_mapping_elements.append(bnf_mapping_object)
	    elif(current_response):
	      current_response.bnf_mapping_elements.append(bnf_mapping_object)
	    bnf_id += 1
		
    elif(group_match):
      current_page = None
      current_question = None
      current_response = None
      current_option = None
      current_option_letter = None
      current_group = elements.Group(group_match.group(1), group_match.group(2))
      groups_tree.insert(current_group.level_attr-1, current_group)
      while(len(groups_tree) > current_group.level_attr):
        groups_tree.pop()

      if(current_group.level_attr != 1):
        groups_tree[current_group.level_attr-2].group_elements.append(current_group)

    elif(page_match):
      current_question = None
      current_response = None
      current_option = None
      current_option_letter = None
      current_page = elements.Page(page_match.group(1))
      current_group.page_elements.append(current_page)
	
    elif(additional_comments):
      current_question = elements.Comment('.'.join(['c', str(comment_id)]))
      current_question.text_elements.append(elements.Text(additional_comments.group(1)))
      if(current_page):
        current_page.comment_ref_attr = current_question.id_attr
      else:
        current_group.comment_ref_attr = current_question.id_attr

      comment_id += 1
    
    elif(question_match):
      current_response = None
      current_option = None
      current_option_letter = None
      question_id = QUESTION_ID_PREFIX
      question_id += question_match.group(1)
      question = elements.Question(question_id)
      current_question = question
      if(current_page): #TODO: there must be a current_page here
        current_page.include_elements.append(elements.Include(question.id_attr))

    elif(question_title):
      if(CDATA_match):
	    question_title_CDATA = deleteCDATAContructs(line[7:])
	    current_question.title_element = question_title_CDATA
      if(question_title.group(1)):
        current_question.title_element = question_title.group(1)
    
    elif(question_indent):
        current_question.indent_attr = question_indent.group(1)
		
    elif(text_tag):
	  if(CDATA_match):
	    text_tag = deleteCDATAContructs(line[6:])
	    if(current_question):
		  current_question.text_elements.append(elements.Text(replace_with_json(text_tag)))
	    elif(current_page):
		  current_page.text_elements.append(elements.Text(replace_with_json(text_tag)))
	    else:
		  current_group.text_elements.append(elements.Text(replace_with_json(text_tag)))
	  elif(current_question):
	    set_text(text_tag, current_question, insert_response)
	  elif(current_page):
	    set_text(text_tag, current_page, insert_response)
	  else:
	    set_text(text_tag, current_group, insert_response)

    elif(response_text_tag):
      if(response_text_tag.group(1)):
        text_content = replace_with_json(response_text_tag.group(1))
        #TODO: set type to json?
        if(current_response):
          current_response.text_elements = [elements.Text(text_content)]
 
    elif(note_tag):
      if(CDATA_match): 
        if(note_tag.group(1)):
          note_content = deleteCDATAContructs(line[6:])
          if(current_option):
		    current_option.note_element = elements.Note(note_content)
		    if(insert_response):
		      current_option.note_element.type_attr = TYPE_ATTR_JSON
          elif(current_response):
		    current_response.note_elements = [elements.Note(note_content)]
		    if(insert_response):
		      current_response.note_elements[-1].type_attr = TYPE_ATTR_JSON
          else:
		    current_question.note_elements = [elements.Note(note_content)]
		    if(insert_response):
		      current_question.note_elements[-1].type_attr = TYPE_ATTR_JSON

      elif(note_tag.group(1)):
		note_content = replace_with_json(note_tag.group(1))
		if(current_option):
		  current_option.note_element = elements.Note(note_content)
		  if(insert_response):
		    current_option.note_element.type_attr = TYPE_ATTR_JSON

		elif(current_response):
		  current_response.note_elements = [elements.Note(note_content)]
		  if(insert_response):
		    current_response.note_elements[-1].type_attr = TYPE_ATTR_JSON

		else:
		  current_question.note_elements = [elements.Note(note_content)]
		  if(insert_response):
		    current_question.note_elements[-1].type_attr = TYPE_ATTR_JSON

    elif(response_note_tag):
      if(response_note_tag.group(1) and current_response):
	    response_note_content = replace_with_json(response_note_tag.group(1))
	    current_response.note_elements = [elements.Note(response_note_content)]
	    if(insert_response):
		  current_response.note_elements[-1].type_attr = TYPE_ATTR_JSON
    
    elif(question_when):
      if(question_when.group(1)):
        csv_when_attr = re.sub(' or ', ',q.', question_when.group(1)) 
        current_question.display_when_attr = QUESTION_ID_PREFIX + csv_when_attr

    elif(question_where):
      if(question_where.group(1)):
        csv_where_attr = re.sub(' or ', ',q.', question_where.group(1)) 
        current_question.display_where_attr = QUESTION_ID_PREFIX + question_where.group(1)

    elif(validation_tag):
      validation = {}
      if(validation_tag.group(1)):
        validation_pairs = validation_tag.group(1).split(";;") #Delimeters are ; and : enclosed in double quotes. Normal ; + : should display correctly
        for validation_pair in validation_pairs:
          validation_pair = validation_pair.split("::")
		  #TODO: should I really remove these spaces?
          validation[re.sub('^( )+|( )+$', '', validation_pair[0])] = re.sub('^( )+|( )+$', '', validation_pair[1])
          
      if current_option:
        current_option.validation_element = elements.Validation(None, validation)

      elif current_response:
        current_response.validation_elements.append(elements.Validation(None, validation))

    elif(response_validation_tag and current_response):
      validation = {}
      if(response_validation_tag.group(1)):
        validation_pairs = response_validation_tag.group(1).split(';;')
        for validation_pair in validation_pairs:
          validation_pair = validation_pair.split('::')
          #TODO: should I really remove these spaces?
          validation[re.sub('^( )+|( )+$', '', validation_pair[0])] = re.sub('^( )+|( )+$', '', validation_pair[1])

      current_response.validation_elements.append(elements.Validation(None, validation))

    elif(blank_line):
      current_question = None
      current_response = None
      current_option = None

    elif(radio_option): #test with CDATA
      if(not current_response):
        current_response = elements.Response('select one')
        current_option_letter = 'A'
        current_question.response_elements.append(current_response)
	  
      if(CDATA_match):
        radioString = deleteCDATAContructs(line)
        option_id = current_question.id_attr + '.' + current_option_letter
        option_text = elements.Text(replace_with_json(radioString, option_id))
      else:	  
        option_id = current_question.id_attr + '.' + current_option_letter
        option_text = elements.Text(replace_with_json(radio_option.group(1), option_id))
	  
      if(cloze_response):
		option_text.type_attr = TYPE_ATTR_JSON
      if(insert_response):
	    option_text.type_attr = TYPE_ATTR_JSON
	  
      option = elements.Option(option_id, None, option_text)
      current_option_letter = chr(ord(current_option_letter) + 1)
      current_response.option_elements.append(option)
      current_option = option

    elif(select_box_option):
      if(not current_response):
        current_response = elements.Response('select multi')
        current_option_letter = 'A'
        current_question.response_elements.append(current_response)
      
      if(CDATA_match):
        switchString = deleteCDATAContructs(line)
        option_id = current_question.id_attr + '.' + current_option_letter
        option_text = elements.Text(replace_with_json(switchString, option_id))
      else:
	    option_id = current_question.id_attr + '.' + current_option_letter
	    option_text = elements.Text(replace_with_json(select_box_option.group(1), option_id))
      if(cloze_response):
        option_text.type_attr = TYPE_ATTR_JSON
      if(insert_response):
        option_text.type_attr = TYPE_ATTR_JSON
		
      option = elements.Option(option_id, None, option_text)
      current_option_letter = chr(ord(current_option_letter) + 1)
      current_response.option_elements.append(option)
      current_option = option
	  
    elif(option_clone and current_option):
	  test = re.sub(" ","",option_clone.group(1)) #addresses a bug that occurred when spaces were in clone statement lines.
	  current_option.clone_attr = test

    elif(textbox_response):
      current_response = elements.Response('textbox')
      current_question.response_elements.append(current_response)

    elif(memo_response):
      current_response = elements.Response('memo')
      current_question.response_elements.append(current_response)

    elif(cloze_response):
      #close_response.group(0) = original text
	  #response_text = outputted text
	  #id_attr = 1.5
	  #TYPE_ATTR_JSON = json
      response_text = elements.Text(replace_with_json(cloze_response.group(0), current_question.id_attr), TYPE_ATTR_JSON)
      current_response = elements.Response('cloze', [response_text])
      current_question.response_elements.append(current_response)

    #elif(insert_response):
    elif(bnf_mapping):
      set_bnf(bnf_mapping, insert_response, bnf_id, current_option, current_response)
      bnf_id += 1
    
    elif(response_bnf_mapping):
      set_bnf(response_bnf_mapping, insert_response, bnf_id, current_option, current_response,True)
      bnf_id += 1
	
    elif(instructions_tag):
      if(CDATA_match):
		completeString = deleteCDATAContructs(line[13:])
		if(current_question):
			set_instructions(current_question, completeString, insert_response)		
		elif(current_page):
			set_instructions(current_page, completeString, insert_response)	
		elif(current_group):
			set_instructions(current_group, completeString, insert_response)
	  
      elif(current_question):
        set_instructions(current_question, line[line.index(':')+1:], insert_response)

      elif(current_page):
        set_instructions(current_page, line[line.index(':')+1:], insert_response)

      elif(current_group):
        set_instructions(current_group, line[line.index(':')+1:], insert_response)
		
		
def set_instructions(current_object, line, insert_response):
  current_object.instructions_elements.append(elements.Instructions(replace_with_json(line)))
  if(insert_response):
    current_object.instructions_elements[-1].type_attr = TYPE_ATTR_JSON

def set_bnf(bnf_mapping, insert_response, bnf_id, current_option, current_response, is_response=False):
  bnf_mapping_object = elements.BnfMapping('b.' + str(bnf_id), replace_with_json(bnf_mapping.group(2)))
  if(bnf_mapping.group(1)):
    raw_bnf_when_attr = re.sub(' ', '', bnf_mapping.group(1))
    bnf_when_attr_list = []
    raw_bnf_when_attr_list = raw_bnf_when_attr.split(',')
    for bnf_when_value in raw_bnf_when_attr_list:
      bnf_when_attr_list.append(QUESTION_ID_PREFIX + bnf_when_value)

    bnf_mapping_object.when_attr = ','.join(bnf_when_attr_list)

  if(insert_response):
    bnf_mapping_object.type_attr = TYPE_ATTR_JSON

  if(current_option and (not is_response)):
    current_option.bnf_mapping_elements.append(bnf_mapping_object)

  elif(current_response):
    current_response.bnf_mapping_elements.append(bnf_mapping_object)

def set_bnf2(bnf_mapping, insert_response, bnf_id, current_option, current_response, fullStatement, is_response=False):
  bnf_mapping_object = elements.BnfMapping('b.' + str(bnf_id),fullStatement)
  if(bnf_mapping.group(1)):
    raw_bnf_when_attr = re.sub(' ', '', bnf_mapping.group(1))
    bnf_when_attr_list = []
    raw_bnf_when_attr_list = raw_bnf_when_attr.split(',')
    for bnf_when_value in raw_bnf_when_attr_list:
      bnf_when_attr_list.append(QUESTION_ID_PREFIX + bnf_when_value)

    bnf_mapping_object.when_attr = ','.join(bnf_when_attr_list)

  if(insert_response):
    bnf_mapping_object.type_attr = TYPE_ATTR_JSON

  if(current_option and (not is_response)):
    current_option.bnf_mapping_elements.append(bnf_mapping_object)

  elif(current_response):
    current_response.bnf_mapping_elements.append(bnf_mapping_object)

def set_text(text_tag, current_object, insert_response):
  if(text_tag.group(1)):
    text_content = replace_with_json(text_tag.group(1))
    current_object.text_elements = [elements.Text(text_content)]
    if(insert_response):
      current_object.text_elements[-1].type_attr = TYPE_ATTR_JSON

