#!/usr/bin/env python3.2

import os,sys,shutil

def copy_tmp_dir():
	srcdir = sys.argv[1]
	if srcdir[-1] == '/':
		tmpname = srcdir[:-1]
		print(tmpname)
	else:
		tmpname = srcdir
	(head, tail) = os.path.split(tmpname)
#	print((head, tail))
	workdir = head+"/tmp"
	os.chdir(head)
	print(os.getcwd())
	# system() is much faster than shutil but unportable
	if 1:
		cmdline = "rm -r tmp && cp -a " + tail + " tmp"
		os.system(cmdline)
	else:
		shutil.rmtree(workdir, ignore_errors=True)
		shutil.copytree(srcdir, workdir, symlinks=True)
	return (workdir,srcdir)


def list_dir(dir):
	list = os.listdir(dir)
	for line in list:
		print(line)

#list_dir(dir)

def walk_dir(dir, topdown=True):
	for root, d, files in os.walk(dir, topdown):
		print(root)
		print(d)
		print(files)
#		for name in files:
#			print(os.path.join(d, name))
#			print name

def remove_src_in_files(root, files):
	if 'include' in root.split('/'):
		return
	for name in files:
		if name[:8] != 'Makefile' and name[:7] != 'Kconfig':
			os.remove(os.path.join(root,name))


def remove_only_built_in_dirs(dir):
	for root, dirs, files in os.walk(workdir, topdown=False):
		#print "-----------------------------"
		#print root
		only_builtin = True
		if "built-in.o" in files:
			for name in files:
				if name[-2:] == ".o" and name != "built-in.o":
					only_builtin = False
					break
			if only_builtin and not dirs:
				if 0: # remove tree
					shutil.rmtree(root)
				else: # remove src files, keep Kconfig and Makefile
					remove_src_in_files(root, files)


def remove_all_non_obj_dir(dir):
	non_obj_list = []
	for root, dirs, files in os.walk(dir, topdown=False):
		for name in dirs:
			dir_name = os.path.join(root, name)[len(workdir)+1:]
			non_obj_list.append(dir_name)
		for name in files:
			path_name = os.path.join(root, name)
			if name == "built-in.o":
				non_obj_list.append(path_name[len(workdir)+1:])
		# some dir has .o, but not have built-in.o
		if "built-in.o" not in files:
			for name in files:
				if name[-2:] == ".o":
					path_name = os.path.join(root, name)
					non_obj_list.append(path_name[len(workdir)+1:]) 					
					break
			
	non_obj_list.sort()
	print("-------- sorted non_obj_list --------")
	for name in non_obj_list:
		to_remove = 1
		if name[-2:] == ".o":
			continue
		for other in non_obj_list:
			if len(other) > len(name):
				if other[-2:] == ".o" and name == other[:len(name)]:
						to_remove = 0
						break

		if to_remove == 1:
			path = os.path.join(workdir, name)
			if "gcov" in name.split('/'):
				print("gcov:"+path)
			if os.path.exists(path):
#				print("remove:"+path)
				# as some Kconfig include unused Kconfig of dir
				# For compile, we should keep
				# For just code reading, we can remove it
				if 0:
					shutil.rmtree(path)
				else:
					for root, dirs, files in os.walk(path, topdown=False):
						remove_src_in_files(root, files)

def handle_special_files():
	special_files = ['arch/x86/syscalls/syscall_32.tbl', \
					'fs/xfs/xfs_sysctl.h', \
					'drivers/hid/usbhid/usbhid.h', \
					'sound/arm/pxa2xx-pcm.h', \
					'drivers/marvell', \
					'fs/exofs',	\
					'arch/arm/boot/dts', \
					'drivers/staging/android',	\
					'arch/arm/tools',	\
					]
	useful_dts = ['pxa', 'sec', 'ske', '88p', 'mmp','Mak']
	for name in special_files:
		srcpath = os.path.join(srcdir, name)
		dstpath = os.path.join(workdir, name)
		print("special file: "+srcpath)
		if os.path.isfile(srcpath) and not os.path.exists(dstpath):
			shutil.copy(srcpath, dstpath)	
		if os.path.isdir(srcpath):
			print("path: "+dstpath+" exist is ", os.path.exists(dstpath))
			shutil.rmtree(dstpath)
			shutil.copytree(srcpath, dstpath, symlinks=True)
			if 'dts' in name.split('/'):
				print("for dts: from"+srcpath+"to"+dstpath)
				for root, dirs, files in os.walk(dstpath, topdown=True):
					for name in files:
						if name[:3] not in useful_dts	\
							and 'include' not in root.split('/'):
							print("remove: "+os.path.join(root, name))
							os.remove(os.path.join(root, name))
			 

workdir,srcdir = copy_tmp_dir()
print("working dir is : " + workdir)
remove_only_built_in_dirs(workdir)

for name in os.listdir(workdir):
	ignored_dir = ["include", "Documentation", "scripts", "tools", "samples"]
	if name not in ignored_dir:
		path_name = os.path.join(workdir, name)
		if os.path.isdir(path_name):
			print("------------------ handled path: "+path_name)
#			print("return value: "+remove_non_built_in_dirs(path_name))
			remove_all_non_obj_dir(path_name)

handle_special_files()
	
		







