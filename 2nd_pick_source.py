#!/usr/bin/env python3.2

import os,sys,shutil,fileinput
	
'''
now we finish the 1st level pruning, Let's step to 2nd level pruning
'''

workdir = '/home/hpyu/ramtmp/tmp'
srcdir = '/home/hpyu/ramtmp/kernel'

to_remove_source_list = []
to_remove_head_list = []
compiled_source_list = []
included_source_list = []

ignored_dirs = ['Documentation', 'firmware', 'samples', 'scripts', 'tools', 'usr']

def init_to_remove_source_list():
	for root, dirs, files in os.walk(workdir, topdown=False):
		for name in files:
			if name[-2:] == '.c' or name[-2:] == '.S':
				path = os.path.join(root[len(workdir)+1:], name)	
				to_remove_source_list.append(path)
	to_remove_source_list.sort()


def init_to_remove_head_list():
	for root, dirs, files in os.walk(workdir, topdown=False):
		for name in files:
			if name[-2:] == '.h':
				path = os.path.join(root[len(workdir)+1:], name)	
				to_remove_head_list.append(path)
	print("headfiles num: %d" % len(to_remove_head_list))
	to_remove_head_list.sort()


def find_compiled_source_list():
	for root, dirs, files in os.walk(workdir, topdown=False):
		if root is not workdir and root.split('/')[5] in ignored_dirs:
			continue
		for name in files:
			if name[-2:] == '.o' and name[0] != '.':
				cname = name[:-1]+'c'
				sname = name[:-1]+'S'
				for name in cname,sname:
					if os.path.exists(os.path.join(root,name)):
						path = os.path.join(root[len(workdir)+1:], name)
						compiled_source_list.append(path)

#	for name in compiled_source_list:
#		print(name)

## file_input is 50% slower than readline
def find_compiled_included_source_list_1(): 
	all_include_lines = []
	stripped_include_lines = []
	for name in compiled_source_list:	
#		with fileinput.input(tuple(os.path.join(workdir, name)) as f:
		pathname = os.path.join(workdir, name)
		#print("pathname: "+pathname)
		try:
			for line in  fileinput.input(pathname):
				if line[0:4] == '#inc':
					pass
					#print(line)
		except UnicodeDecodeError:
			print("ignore "+pathname)
			fileinput.close()


def add_local_include_csh_to_source_list(local_includes):
	for name in local_includes:
		dirname = os.path.dirname(name.split('"')[0])
		headname = name.split('"')[1]
		fullname = os.path.join(dirname, headname)

#		print("fullname: ", fullname)
		if headname[0] == '.':
			nlist = fullname.split("/")
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
		else:
			realname = fullname

#		print("realname: ", realname)
		if realname[-2:] == '.c' or realname[-2:] == '.S':
			if realname not in compiled_source_list:
				compiled_source_list.append(realname)
		elif realname[-2:] == '.h':
			if realname not in included_source_list:
				included_source_list.append(realname)


def add_sys_include_h_to_head_list(sys_includes):
	sys_inc_list = []
	for name in sys_includes:
		headname  = name.split('<')[1]
		headname  = headname.split('>')[0]
		# some inlcude is used by scripts/usr/tools x86 code, ignore them
		if '/' not in headname:
			pass
		else:
			sys_inc_list.append(headname)

	sys_inc_list.sort()
	for name in sys_inc_list:
		fst_dir = name.split('/')[0]
		incpath = os.path.join(workdir, 'include', fst_dir)
		if os.path.exists(incpath):
			realname = os.path.join('include', name)
			included_source_list.append(realname)
			#print("append: ", realname)
		else:
			if name[:3] == 'asm':
				realname = os.path.join('arch/arm/include', name)
				included_source_list.append(realname)
				print("append: ", realname)
			elif name[:4] in ['mach', 'plat']:
				findpath = 0
				armdir = os.path.join(workdir, "arch/arm")
				for root, dirs, files in os.walk(armdir):
					for f in files:
						rootbase = os.path.basename(root)
						if f[-2:] == '.o' and rootbase[:4] == name[:4]:
							findpath = 1
							realname = os.path.join(root[len(workdir)+1:],'include', name)	
							included_source_list.append(realname)
							print("append: ", realname)
							break
					if findpath == 1:
						break



def find_included_source_list(file_list):
	system_include_lines = []
	local_include_lines = []
	stripped_include_lines = []
	for name in file_list:
		try:
			pathname = os.path.join(workdir, name)
			f = open(pathname, 'r')
			for line in f.readlines():
				if line[:4] == '#inc':
					if line[9] == '<':
						system_include_lines.append(line)
					elif line[9] == '"':
						prefix = name+line[8:]	
						local_include_lines.append(prefix)
		except UnicodeDecodeError:
			print("ignore "+pathname)
			f.close()
		except IOError:
			continue

	for line in system_include_lines:
		if line not in stripped_include_lines:
			stripped_include_lines.append(line)

	add_local_include_csh_to_source_list(local_include_lines)
	add_sys_include_h_to_head_list(stripped_include_lines)



def restore_ignored_dirs():
	for name in ignored_dirs:
		srcpath = os.path.join(srcdir,name)
		dstpath = os.path.join(workdir,name)
		shutil.rmtree(dstpath, ignore_errors=True)
		print("restore: "+ dstpath)
		shutil.copytree(srcpath, dstpath, symlinks=True)

def remove_files():

	for name in compiled_source_list:
		if name in to_remove_source_list:
			to_remove_source_list.remove(name)

	for name in included_source_list:
		if name in to_remove_head_list:
			to_remove_head_list.remove(name)

	for name in to_remove_source_list:
		fullname = os.path.join(workdir, name)
		if os.path.exists(fullname):
			#print("source remove: "+fullname)
			os.remove(fullname)

	for name in to_remove_head_list:
		fullname = os.path.join(workdir, name)
		if os.path.exists(fullname):
			#print("head remove: "+fullname)
			#os.remove(fullname)
			pass

	restore_ignored_dirs()

def copy_special_files():
	special_source_files = ['arch/arm/tools/gen-mach-types',  \
							'arch/arm/kernel/asm-offsets.s',   \
							'kernel/bounds.s',   \
							'kernel/bounds.c',   \
							'arch/arm/kernel/asm-offsets.c',   \
							'arch/arm/include/asm/entry-macro-multi.S',   \
							'arch/arm/include/debug/pxa.S',   \
							'arch/arm/include/asm/hardware/debug-8250.S',   \
							'drivers/usb/gadget/storage_common.c',   \
							'lib/gen_crc32table.c',   \
							'arch/arm/kernel/vmlinux.lds',   \
							'arch/arm/kernel/vmlinux.lds.S',   \
							]
	for name in special_source_files:
		srcpath = os.path.join(srcdir, name)
		dstpath = os.path.join(workdir, name)
		shutil.copy(srcpath, dstpath)

## main process ##

init_to_remove_source_list()
init_to_remove_head_list()

find_compiled_source_list()

find_included_source_list(compiled_source_list)

find_included_source_list(included_source_list)

remove_files()
copy_special_files()




