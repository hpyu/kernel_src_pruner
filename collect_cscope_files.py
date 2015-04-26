#!/usr/bin/env python

__metatype__ = type # new type class
class wraper:
	def __init__(self):
		self.srcroot = None
		self.objroot = None
		self.file_map = {}
		self.file_list = []
		self.final_map = {}

	def save_list_to_file(self, filename, listname):
		f = open(filename,'w')
		for line in listname:
			f.writelines(line)
			f.writelines("\n")
		f.close()

	def collect_src(self, fname):
		f = open(fname, 'r')
		for line in f.readlines():
			line = line.replace(')', ' ')
			line = line.replace('\n', ' ')
			llist = line.split(' ')
			for item in llist:
				if item[-2:] in ['.h', '.c', '.S']:
					self.file_map.setdefault(item,True)
					
		f.close()
	
	def make_cscope_files(self):
		for fname in list(self.file_map.keys()):
			if '..' in fname:
				fname = normpath(fname) 

			if fname[0] == '/':
				if fname[0:len(self.srcroot)] == self.srcroot:
					fname = fname[len(self.srcroot)+1:]
					self.final_map.setdefault(fname,True)
			else:
				self.final_map.setdefault(fname,True)
				
		for name in list(self.final_map.keys()):
			if not exists(join(self.srcroot, name)):
				if not exists(join(self.objroot, name)):
					#printf("%s  not exists" % name)
					continue
				else:
					self.file_list.append(join(self.objroot, name))
			else:
				self.file_list.append(name)

		self.file_list.sort()

		self.save_list_to_file(join(self.srcroot, "cscope.files"), self.file_list)
		printf("%s is created in srcroot." % "cscope.files")
	

def main():
	p = wraper()

	if (len(sys.argv) < 3):
		printf("Usage: python %s kernel_src_path kernel_obj_path" % sys.argv[0])
		sys.exit("invalid params")

	p.srcroot = abspath(sys.argv[1])
	p.objroot = abspath(sys.argv[2])

	for path in [p.srcroot, p.objroot]:
		if not exists(path):
			sys.exit("%s dosen't exist" % path)

	printf("srcroot: %s" % p.srcroot)
	printf("objroot: %s" % p.objroot)

	for rootdir, pathlist, filelist in os.walk(p.objroot):
		for fname in filelist:
			if fname[-4:] == '.cmd':
				fname = join(rootdir, fname)
				p.collect_src(fname)

	p.collect_src(join(p.objroot, '.missing-syscalls.d'))
	p.make_cscope_files()
	

if __name__ == '__main__':
	# Python2.x & 3.x compatible
	from distutils.log import warn as printf
	from os.path import *
	import os,sys,shutil,getopt
	main()

	

