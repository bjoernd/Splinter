#!/usr/bin/python

# SPLint output colorizer
#
# This script runs SPLint with a given set of arguments and colorizes the
# output to improve readability.

import sys
import os
import re

# Colors for printing
colors = {
	'red' 		: '\033[31m',
	'green' 	: '\033[32m',
	'yellow'	: '\033[33m',
	'blue'  	: '\033[34m',
	'magenta'	: '\033[35m',
	'cyan'  	: '\033[36m',
	'white'     : '\033[37m'
}

# This is where the compiled regexes will get stored soon
regexes = {}

# Hook to colorize the Splint title line. This is useful, because it helps you
# find the beginning of last run's output.
def title_hook(line):
	print colors["green"]
	x = "#" * len(line)
	print x
	print line
	print x + "\033[0m"

# Hook to colorize Splint's function names
def funcname_hook(line):
	fre = re.compile("(.*\(in function )(.*)(\).*)")
	obj = fre.match(line)
	if (obj is not None):
		print obj.group(1) + colors["magenta"] + obj.group(2) + "\033[0m" + obj.group(3)

# Hook to colorize error messages
def error_hook(line):
	print colors["red"] + line + "\033[0m"

# Hook to colorize explainatory text
def explaination_hook(line):
	print colors["blue"] + line + "\033[0m"

def info_hook(line):
	print colors["cyan"] + line + "\033[0m"

hooks = {
	'title' : title_hook,
	'funcname' : funcname_hook,
	'error' : error_hook,
	'expl' : explaination_hook,
	'info' : info_hook
}

# Uncompiled regexes. This is what we look for in Splint's output and then
# call hook functions (see @hooks below...) to do whatever we want with this
# line
regex_uncompiled = {
	'title' : "Splint \d\..*",
	'funcname' : ".*\(in function .*\).*",
	'error' : "\s{4,4}\S.*",
	'expl' : "\s{2,2}\S.*",
	'info' : "Command Line:.*"
}

### START OF SCRIPT ###

# Compile the regexes
for reg in regex_uncompiled.keys():
	regexes[reg] = re.compile(regex_uncompiled[reg])

# build cmd line
cmdline = ""
for param in sys.argv[1:]:
	cmdline += (" " + param)

print "Executing: ", cmdline

# Output will be redirected
# XXX: I'd prefer to read the output directly into this script?
cmdline += " >&_splint.out"

# execute splint
os.system(cmdline)

# read output and remove temp file
f = file("_splint.out")
output = f.readlines()
os.system("rm _splint.out")

# process output
for line in output:
	# erase trailing newline
	l = line.strip("\n")

	seen = 0
	# try to match this line with a regex
	for name in regexes:
		if regexes[name].match(l):
			seen = 1
			hooks[name](l)
			break
	# if no regex matched, simply print
	if seen == 0:
		print l
