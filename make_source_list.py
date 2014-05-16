#!/usr/bin/env python3.2

import os,sys,shutil

opened_file_list = []
opened_file_list2 = []
source_list = []

if len(sys.argv) < 5:
	print("Usage %s opened_files.txt kernel_dir link_dir source_list" % sys.argv[0])
	sys.exit()

strace_log = sys.argv[1]
srcpath = os.path.normpath(sys.argv[2])
dstpath = os.path.normpath(sys.argv[3])
source_list_name = sys.argv[4]

def save_list_to_file(filename, listname):
	f = open(filename,'w')
	for name in listname:
		f.writelines(name)
		f.writelines("\n")
	f.close()
		

def make_opened_file_list():
	try:
		f = open(strace_log, 'r')
		for line in f.readlines():
			line_list = line.split(" ")
			if line_list[1][:4] == "open" and '-1' not in line_list:
				fname = line.split("\"")[1]
				if fname[0] != '/' or fname[0:len(srcpath)] == srcpath:
					if fname[0:len(srcpath)] == srcpath:
						fname = fname[len(srcpath)+1:]

					if fname not in opened_file_list and \
						fname[-2:] not in ['.o', '.d'] and \
						fname[-4:] not in ['.cmd', '.tmp'] and \
						fname not in opened_file_list:
						opened_file_list.append(fname)
		
		opened_file_list.sort()
		#print("len :%d" % len(opened_file_list))
		for name in opened_file_list:
			if len(name.split('..')) > 1:
				#print(name)
				nlist = name.split("/")
				pos = 0 
				start = 0 
				num = 0 
				while pos < len(nlist):
					if nlist[pos] == '..':
						if start == 0:
							start = pos 
						num += 1
					pos += 1
				if start - num == 0:
					realname = '/'.join(nlist[start+num:])
				else:
					nlist = nlist[0:start-num]+nlist[start+num:]
					realname = '/'.join(nlist)
				#print("realname: "+realname)
				opened_file_list2.append(realname)
			else:
				opened_file_list2.append(name)

#		save_list_to_file("opened_file_list.txt", opened_file_list)
#		save_list_to_file("opened_file_list_2.txt", opened_file_list2)
		for name in opened_file_list2:
			if name[-2:] in ['.c', '.S', '.h']:
				source_list.append(name)
		save_list_to_file(source_list_name, source_list)

	except IOError:
		sys.exit()


def make_list_and_linkdir():
	if os.path.exists(dstpath):
		print("remove "+dstpath)
		shutil.rmtree(dstpath)
	
	os.makedirs(dstpath, mode=0o777)

	for root, dirs, files in os.walk(srcpath,topdown=True, followlinks=True):
		relpath = root[len(srcpath)+1:]
		#print("root: "+root)
		#print(dirs)
		dirname = os.path.join(dstpath,relpath)
		if not os.path.exists(dirname):
			os.makedirs(dirname)
		
		for name in files:
			linkname = os.path.join(dstpath,relpath,name)
			srcname = os.path.join(root, name)
			if not os.path.exists(linkname):
				os.symlink(srcname, linkname)

	for root, dirs, files in os.walk(dstpath,topdown=True):
		for name in files:
			relpath = os.path.join(root[len(dstpath)+1:], name)
			if relpath[-2:] in ['.c', '.h', '.S']:
				if relpath not in opened_file_list2:
					rmname =  os.path.join(root, name)
					#print("remove: "+rmname)
					os.remove(rmname)
			
	
def copy_missed_files():
	#hz.h is just called by stat(), and only this files is missed
	#so handle it here to reduce time
	missed_files = ['include/config/hz.h']		
	for name in missed_files:
		sname = os.path.join(srcpath, name)
		lname = os.path.join(dstpath, name)
		os.symlink(sname, lname)
		

make_opened_file_list()
make_list_and_linkdir()
copy_missed_files()


