#!/usr/bin/env python
# Python2.x and 3.x compatible

'''
Author  : Haipeng Yu
Email   : hpyu@marvell.com
Function: make precise cscope.files and clean kernel tree without redundant files
Usage   : python somewhere/kernel_pruner.py -f strace_log.txt -s origpath/kernel -d  dstpath/k
Usage   : python somewhere/kernel_pruner.py -f strace_log.txt
        : ctags -R -L cscope.files && cscope -Rbqk

Date    : 2015.4
'''

def extract_fname(line, srcroot):
	line_list = line.split("\"")
	if len(line_list) > 2:
		fname = line_list[1]
		if fname[0] != '/' or fname[0:len(srcroot)] == srcroot:
			if fname[0:len(srcroot)] == srcroot:
				fname = fname[len(srcroot)+1:]

			if exists(os.path.join(srcroot, fname)) and \
				fname[-2:] not in ['.o', '.d'] and \
				fname[-4:] not in ['.cmd', '.tmp']:
				return fname
	return ""

def extract_opened_files(p):
	try:
		f = open(p.strace_log, 'r')
		for line in f.readlines():
			if " -1 " not in line:
				name = extract_fname(line, p.srcroot)
				p.file_map.setdefault(name,True)

		for name in p.file_map.keys():
			if name.find('..') != -1:
				p.opened_files.setdefault(normpath(name),True)
			else:
				p.opened_files.setdefault(name,True)

	except IOError as e:
		printf(e)
		sys.exit()

def build_clean_tree(p):
	if exists(p.dstroot):
		shutil.rmtree(p.dstroot)
	
	os.makedirs(p.dstroot, mode=0o777)
		
	for name in p.opened_files.keys():
		src = join(p.srcroot, name)
		dst = join(p.dstroot, name)

		if not exists(os.path.dirname(dst)):
			os.makedirs(dirname(dst), mode=0o777)
		#	os.mkdir(dst, mode=0o777, dir_fd=None)

	for name in p.opened_files.keys():
		src = join(p.srcroot, name)
		dst = join(p.dstroot, name)

		if isfile(src) and not os.path.exists(dst):
			if p.link:
				os.symlink(src, dst)
			else:
				shutil.copyfile(src, dst)
				shutil.copymode(src, dst)
			
def usage():
	help_info = [
		"Usage:",
		"	steps::",
		"	1, setup cross compiling environmet for kernel",
		"	2, source make_tags.sh your_proj_defconfig",
		"	to generate a clean kernel tree:",
		"	3, python somewhere/kernel_pruner.py -f strace_log.txt -s origpath/kernel -d  dstpath/k",
		"",
		"	Options:",
		"	-f strace_log -- output file of strace",
		"	-s srcdir -- original kernel path,",
		"	-d dstdir -- pruned kernel path,",
		"	-h -- help info,",
		"	-l -- create symbol link for all files,",
		"",
		"	README.txt for more info",
	]

	for line in help_info:
		printf(line)
	
	sys.exit()


__metatype__ = type # new type class

class wraper:
	def __init__(self):
		self.opened_files = {}
		self.file_map = {}
		self.strace_log = None
		self.srcroot = abspath('.')
		self.dstroot = None
		self.link = False
		self.cscope_files_only = False

	def check_options(self):
		return

	def check_dstroot(self):
		if self.dstroot == None:
			self.cscope_files_only = True
		else:
			if exists(self.dstroot):
				printf("%s exited!" % self.dstroot)
				if sys.version[0] < '3':
					rm = raw_input("Enter Y if you agree to remove:")
				else:
					rm = input("Enter Y if you agree to remove:")
				if rm in ['y', 'Y']:
					shutil.rmtree(self.dstroot)
				else:
					printf("Exit because not agree to remove " + self.dstroot)
					sys.exit()

			os.makedirs(self.dstroot, mode=0o777)

	def save_list_to_file(self, filename, listname):
		f = open(filename,'w')
		for line in listname:
			f.writelines(line)
			f.writelines("\n")
		f.close()

	def dump_to_files(self):
		source_list = []

		flist = list(self.opened_files.keys())
		flist.sort()

#		self.save_list_to_file("cscope.files", flist)
#		printf("save all file list to cscope.files")

		for name in self.opened_files.keys():
			if name[-2:] in ['.c', '.S', '.h']:
				source_list.append(name)
		source_list.sort()
		self.save_list_to_file("cscope.files", source_list)
		printf("save .c .S .h files to cscope.files")

def main():

	p = wraper()

	try:
		opts, args = getopt.getopt(sys.argv[1:], "hf:s:d:l")
		for opt, arg in opts:
			if opt == '-h':
				usage()
			elif opt == '-f':
				p.strace_log = arg
			elif opt == '-s':
				p.srcroot = abspath(arg)
			elif opt == '-d':
				p.dstroot = abspath(arg)
			elif opt == '-l':
				p.link = True
			else:
				printf("Ignore invalid opt:%s\n" % opt)

		printf("srcdir: %s" % p.srcroot)
		printf("dstdir: %s" % p.dstroot)
		printf("strace file: %s" % p.strace_log)

	except getopt.GetoptError:
		usage()

	p.check_dstroot()

	if p.strace_log == None:
		usage()

	extract_opened_files(p)

	p.dump_to_files()

	if not p.cscope_files_only:
		build_clean_tree(p)

if __name__ == '__main__':
	# Python2.x & 3.x compatible
	from distutils.log import warn as printf
	from os.path import *
	import os,sys,shutil,getopt
	main()

