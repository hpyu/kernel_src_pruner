#!/bin/bash

#This is a wrapper of kernel_pruner
#It make tags with one command
#User should setup cross compiling environment firstly

if [[ -z "$1" || -z "$2" ]]; then
	echo "Usage:\n\tsource make_tags.sh path/kernel_pruner.py your_proj_defconfig"
	echo "\n\tor\n\tsource make_tags.sh path/kernel_pruner.py your_proj_defconfig dstdir" 
	return
fi

echo "defconfig: $2"
syscalls=rename,stat,lstat,mkdir,openat,getcwd,chmod,access,faccessat,readlink,unlinkat,statfs,unlink,open,execve,newfstatat
strace -f -o /tmp/mrproper_files.txt -e trace=$syscalls -e signal=none make mrproper
strace -f -o /tmp/defconfig_files.txt -e trace=$syscalls -e signal=none make $2
strace -f -o strace_log.txt -e trace=$syscalls -e signal=none make -j8
cat /tmp/defconfig_files.txt >> strace_log.txt
cat /tmp/mrproper_files.txt >> strace_log.txt

python $1 -f strace_log.txt

if [ -n "$3" ]; then
python $1 -f strace_log.txt -s . -d $3
fi

if [ -n "$4" ]; then
python $1 -f strace_log.txt -s . -d $3 $4
fi

cp -f cscope.files cs.files
ctags -R -L cscope.files && cscope -Rbqk


