'''
	[hpyu] 2015.4.8
	Re-struct the code, remove global varibles
	time python3.2 make_source_list.py -f ~/ramtmp/kernel/strace_log.txt -s ~/ramtmp/kernel -d  ~/ramtmp/k
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

		p.dump_to_files()

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

		if islink(src):
			printf(src + " is a link")

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
	help_info = {
		"Usage:",
			"-f strace_log -- output file of strace",
			"-s srcdir -- original kernel path,",
			"-d dstdir -- pruned kernel path,",
			"-h -- help info,",
			"-l -- create symbol link for all files,",
			"-c -- craete compiling script",
	}

	for line in help_info:
		printf(line)
	
	sys.exit()

def create_compiling_script(p):
	set_env_sh = [
		'export PATH=:$PATH:/usr/local/prebuilts/gcc/linux-x86/aarch64/aarch64-linux-android-4.8/bin',
		'export CROSS_COMPILE=aarch64-linux-android-',
		'export ARCH=arm64',
	]

	compile_sh = [
		'syscalls=rename,stat,lstat,mkdir,openat,getcwd,chmod,access,faccessat,readlink,unlinkat,statfs,unlink,open,execve,newfstatat',
		'strace -f -o mrproper_files.txt -e trace=$syscalls -e signal=none make mrproper',
		'strace -f -o defconfig_files.txt -e trace=$syscalls -e signal=none make pxa1908_j1lte_eur_defconfig',
		'strace -f -o strace_log.txt -e trace=$syscalls -e signal=none make -j8',
		'cat defconfig_files.txt >> strace_log.txt',
		'cat mrproper_files.txt >> strace_log.txt',
	]

	p.save_list_to_file("set_env.sh", set_env_sh)
	p.save_list_to_file("compile.sh", compile_sh)



__metatype__ = type # new type class

class wraper:
	def __init__(self):
		self.opened_files = {}
		self.file_map = {}
		self.strace_log = None
		self.srcroot = None
		self.dstroot = None
		self.link = False
		self.script = False

	def check_options(self):
		if self.strace_log == None or self.srcroot == None or self.dstroot == None:
			usage()

	def save_list_to_file(self, filename, listname):
		f = open(filename,'w')
		for line in listname:
			f.writelines(line)
			f.writelines("\n")
		f.close()

	def dump_to_files(self):
		source_list = []

		l = list(self.file_map.keys())
		l.sort()
		self.save_list_to_file("file_map.txt", l)
		l2 = list(self.opened_files.keys())
		l2.sort()
		self.save_list_to_file("opened_files.txt", l2)

		for name in self.opened_files.keys():
			if name[-2:] in ['.c', '.S', '.h']:
				source_list.append(name)
		source_list.sort()
		self.save_list_to_file("source_list.txt", source_list)

def main():

	p = wraper()

	try:
		opts, args = getopt.getopt(sys.argv[1:], "hf:s:d:lc")
		for opt, arg in opts:
			if opt == '-h':
				usage()
			elif opt == '-f':
				p.strace_log = arg
			elif opt == '-s':
				p.srcroot = normpath(arg)
			elif opt == '-d':
				p.dstroot = normpath(arg)
			elif opt == '-l':
				p.link = True
			elif opt == '-c':
				p.script = True
			else:
				printf("Ignore invalid opt:%s\n" % opt)

	except getopt.GetoptError:
		usage()
	
	if p.script:
		create_compiling_script(p)

	p.check_options()

	if exists(p.dstroot):
		printf("%s exited!" % p.dstroot)
		if sys.version[0] < '3':
			rm = raw_input("Enter Y if you agree to remove:")
		else:
			rm = input("Enter Y if you agree to remove:")
		if rm in ['y', 'Y']:
			shutil.rmtree(p.dstroot)
		else:
			printf("Exit because not agree to remove " + p.dstroot)
			sys.exit()

	os.makedirs(p.dstroot, mode=0o777)
	extract_opened_files(p)
	build_clean_tree(p)

if __name__ == '__main__':
	# Python2.x & 3.x compatible
	from distutils.log import warn as printf
	from os.path import *
	import os,sys,shutil,getopt
	main()

