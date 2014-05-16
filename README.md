kernel_src_pruner
=================

This tool can remove all non-compiled c/h/S files of kernel source tree, and list all used c/h/S files, written by Python.
The generated source list can help make a mininal vim/tag or SourceInsight project, make the symbol searching more accurate.

Usage of kernel_src_pruner

1, compile kernell with strace
	 strace -o opened_kernel_files.txt -f -e trace=open make
2, ./make_source_list.py opened_files.txt kernel_dir link_dir source_list
	It will generate a source_list used to setup ctags/cscope/sourceinsight project,
	and a link_dir with only used c/h/S files and other compiling needed files, all files are symbol links

