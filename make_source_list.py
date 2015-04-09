'''
	[hpyu] 2015.4.8
	Re-struct the code, remove global varibles
	time python3.2 make_source_list.py ~/ramtmp/kernel/strace_log.txt ~/ramtmp/kernel ~/ramtmp/k
'''

def save_list_to_file(filename, listname):
	f = open(filename,'w')
	for name in listname:
		f.writelines(name)
		f.writelines("\n")
	f.close()

def dump_to_files(file_map, opened_files):
	source_list = []

	l = list(file_map.keys())
	l.sort()
	save_list_to_file("file_map.txt", l)
	l2 = list(opened_files.keys())
	l2.sort()
	save_list_to_file("opened_files.txt", l2)

	for name in opened_files.keys():
		if name[-2:] in ['.c', '.S', '.h']:
			source_list.append(name)
	source_list.sort()
	save_list_to_file("source_list.txt", source_list)
	
def copy_source_tree(srcroot, dstroot):
	for root, dirs, files in os.walk(srcroot,topdown=true, followlinks=true):
		relpath = root[len(srcroot)+1:]
		#print(dirs)
		dirname = join(dstroot,relpath)
		if not exists(dirname):
			os.makedirs(dirname)
		
		for name in files:
			linkname = join(dstroot,relpath,name)
			srcname = join(root, name)
			if not exists(linkname):
				os.symlink(srcname, linkname)

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

def extract_opened_files(strace_log, opened_files, srcroot):
	file_map = {}

	try:
		f = open(strace_log, 'r')
		for line in f.readlines():
			if " -1 " not in line:
				name = extract_fname(line, srcroot)
				file_map.setdefault(name,True)

		for name in file_map.keys():
			if name.find('..') != -1:
				opened_files.setdefault(normpath(name),True)
			else:
				opened_files.setdefault(name,True)

		dump_to_files(file_map, opened_files)

	except IOError as e:
		printf(e)
		sys.exit()

def build_clean_tree(opened_files, srcroot, dstroot):
	if exists(dstroot):
		shutil.rmtree(dstroot)
	
	os.makedirs(dstroot, mode=0o777)
		
	for name in opened_files.keys():
		src = join(srcroot, name)
		dst = join(dstroot, name)

		if not exists(os.path.dirname(dst)):
			os.makedirs(dirname(dst), mode=0o777)
		#	os.mkdir(dst, mode=0o777, dir_fd=None)

		if islink(src):
			printf(src + " is a link")

	for name in opened_files.keys():
		src = join(srcroot, name)
		dst = join(dstroot, name)

		if isfile(src) and not os.path.exists(dst):
			shutil.copyfile(src, dst)
			shutil.copymode(src, dst)
			

def main():
	opened_files = {}

	if len(sys.argv) < 4:
		printf("Usage: %s strace_log src_dir dst_dir" % sys.argv[0])
		sys.exit()

	strace_log = sys.argv[1]
	srcroot = normpath(sys.argv[2])
	dstroot = normpath(sys.argv[3])
	
	if exists(dstroot):
		printf("remove "+dstroot)
		rm = input(dstroot + " exists, enter Y if you agree to remove:")
		if rm in ['y', 'Y']:
			shutil.rmtree(dstroot)
		else:
			printf("Exit because not agree to remove " + dstroot)
			sys.exit()

	os.makedirs(dstroot, mode=0o777)
	extract_opened_files(strace_log, opened_files, srcroot)
	build_clean_tree(opened_files, srcroot, dstroot)

if __name__ == '__main__':
	# Python2.x & 3.x compatible
	from distutils.log import warn as printf
	from os.path import *
	import os,sys,shutil
	main()

