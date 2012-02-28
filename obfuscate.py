import string # for string.ascii_lowercase
import re # for lots of regex-iness!
import os # for path stuff
import shutil # for copying

i = 0 # current obfuscatey thing
s = '' # current file contents

def toB26(n): # convert a number to base 26 using letters
	s = '' # output string
	while True: # infinite loop
		s = string.ascii_lowercase[n % 26] + s # add next character to string
		n //= 26 # div by 26
		if n <= 0: # if n is 0 or less converting is done
			break
	return s # return generated string

def build(m): # build next letter thingy from word found
	global i, s # global vars needed
	w = m.group(0).lower() # get the word found
	if not dc.has_key(w): # if word isn't already converted
		dc[w] = toB26(i) # convert word and add it to dictionary
		i += 1 # increment i
		while re.search(r'\b' + toB26(i) + r'\b', s): # increment i until not conflicting with anything
			i += 1
	return ' ' + dc[w] + ' ' # return new word with padding (for replacing)

def obfuscate(fname, backup): # method to obfuscate a file (fname = file, backup = whether to place obfuscation in new file)
	global i, s # global vars needed
	f = open(fname, 'r') # open the file for reading
	s = f.read() # get file contents into s

	s = re.sub('//.*\n', '\n', s) # remove in-line comments
	s = re.sub(r'{[^$]*?}', '', s) # remove block comments which aren't compiler directives
	s = re.sub(r'{\$macro\s+on}', '', s) # remove macro compiler directives

	strs = [] # strings to not change

	i = 0 # reset current i count
	while re.search(r'\b' + toB26(i) + r'\b', s): # increment i until not conflicts
		i += 1

	s = re.sub(r'(?:\b[a-zA-Z_]+\b)' + radd, build, s) # this is where the magic happens 
	# (finds all valid keywords/vars/symbols then calls the build function on them
	# allowing the dictionary adding and then replacing from what build returns)

	for k, v in dc.iteritems(): # add a define for each keyword/var replaced
		s = '{$define ' + v + ':= ' + k + '}\n' + s

	for st in strs: # re-add the strings and compiler directives
		s = re.sub('#####', st, s, 1)

	s = '{$macro on} \n' + s # add the macro compiler directive needed
	s = re.sub('\n', ' ', s) # remove new lines
	s = re.sub(r'\s+', ' ', s) # shorten all whitespace to just 1 space

	f.close() # close the file
	if backup: # if in a new file
		f = open(fname + '_obf', 'w') # create/overwrite an obfuscated version of the file
		f.write(s) # write the new data
		f.close() # close the file
	else: # if not a new file
		f = open(fname, 'w') # open the old file with write provileges
		f.write(s) # re-write file with data
		f.close() # close

syms = [':=', ':', ';', ',', '\[', '\]', '\{', '\}', '\(', '\)', '<>', '>=', '<=', '<', '>', '=', '\+', '-', '\*', '/', '\.\.', '\.'] # symbols that can be replaced
radd = '' # to add to build regex
for sym in syms: # iterate symbols
	radd += '|' + sym # add to extra regex stuff

dc = {} # dictionary of replaced stuff

fname = raw_input('Input pascal code file name and path: ') # get file/directory to obfuscate

if os.path.exists(fname): # if it exists
	if os.path.isfile(fname): # if is a file
		obfuscate(fname, True) # obfuscate into new file
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
					obfuscate(filename, False) # obfuscate into same file
					print 'Derped on ' + filename # print file changed
					c += 1 # increment count
		if c > 0: # if has obfuscated anything
			print 'And he derped on ALL the files! (' + str(c) + ')' # print amount of files obfuscated
		else: # no files
			print 'No pascal files found' # say that
else: # path didn't exist
	print 'Path does not exist!' # print path doesn't exist