import re
import os
import shutil

def deobfuscate(fname, backup): # method to de-obfuscate a file (fname = file, backup = whether to place obfuscation in new file)
	f = open(fname, 'r') # open file for reading
	s = f.read() # get contents as string

	strs = [] # strings and compiler directives to not erase (or de-obfuscate with)

	for match in re.finditer(r"(?:'(?:[^'\\]|\\.)*'|{\$.*?})", s): # find all strings and compiler directives
		strs += [match.group(0)] # add to string array
	s = re.sub(r"(?:'(?:[^'\\]|\\.)*'|{\$.*?})", '#####', s) # replace with a temporary place-holder

	for st in strs: # loop the strings in the array
		search = re.match(r'{\$define\s+([a-zA-Z]+)\s*:=\s*(.*?)}', st) # if is a define compiler directive
		if search:
			s = re.sub(r'\b' + search.groups()[0] + r'\b', search.groups()[1], s) # replace the defined values
	
	for st in strs: # loop the strings in array (needed to do replace first)
		s = re.sub('#####', st if not re.match(r'{\$define\s+([a-zA-Z]+)\s*:=\s*(.*?)}', st) else '', s, 1) # replace the temporary place-holder with either the string or non-define compiler directive

	s = re.sub(r'{\$macro\s+on}', '', s) # remove macro compiler directives
	s = re.sub(r'\s+', ' ', s) # shorten all whitespace to just 1 space

	f.close() # close the file
	if backup: # if in a new file
		f = open(fname + '_deobf', 'w') # create/overwrite a de-obfuscated version of the file
		f.write(s) # write the new data
		f.close() # close the file
	else: # if not a new file
		f = open(fname, 'w') # open the old file with write provileges
		f.write(s) # re-write file with data
		f.close() # close

fname = raw_input('Input pascal code file name and path: ')

if os.path.exists(fname): # if it exists
	if os.path.isfile(fname): # if is a file
		deobfuscate(fname, True) # obfuscate into new file
	elif os.path.isdir(fname): # if is a directory
		dest = './derpbackup' + re.sub(r'\\', '/', re.sub(r'^([^\\/])', r'/\1', re.sub('(?:[a-zA-Z]:)?', '', re.sub('(?:\\|/)$', '', os.path.abspath(fname))))) # create local backup path
		while os.path.exists(dest): # while local backup with that name exists
			dest += '_' # add underscores
		shutil.copytree(fname, dest) # copy target folder into local backup (obfuscating a whole student's project folder is too trolly to not allow reversing)
		dirn = os.walk(fname) # get recursiveness from directory
		c = 0 # reset file found count
		for d1, rubbish, d2 in dirn: # for all path stuff in directory
			for filen in d2: # for each file in the path stuff
				filename = os.path.join(d1, filen) # create nice filename
				if filename[-4:].lower() == '.dpr' or filename[-4:].lower() == '.pas' or filename[-4:].lower() == '.lpr': # if file-name means it's a pascal/delphi file
					deobfuscate(filename, False) # obfuscate into same file
					print 'Derped on ' + filename # print file changed
					c += 1 # increment count
		if c > 0: # if has obfuscated anything
			print 'And he derped on ALL the files! (' + str(c) + ')' # print amount of files obfuscated
		else: # no files
			print 'No pascal files found' # say that
else: # path didn't exist
	print 'Path does not exist!' # print path doesn't exist