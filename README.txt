h1. Introduction 

Here are 2 python scripts who can generated precise cscope.files and 
a clean kernel tree without redundant files.
The cscope.files is used to create ctags & cscope tags, and  helps save your 
time and patience when searching kernel symbols.

You can get it by:
git clone https://github.com/hpyu/kernel_src_pruner.git

*collect_cscope_files.py* makes cscope.files based on *.o.cmd, it works in 
2s(i7-3770 8 cores). *For most users, this script is enough.*

*kernel_pruner.py* can make cscope.files and a clean kernel tree, it's based on 
strace, works in 12s(i7-3770 8 cores), user can use it if interested on make 
a clean kernel tree.
*make_tags.sh* is a wraper of kernel_pruner.py,it makes cscope.files or a clean 
kernel tree in a single line command.

You can send mail to *hpyu@marvell.com* for any question about them,
I'm willing to improve it with your suggestion.

h1. Usage
  h3. 1. collect_cscope_files.py
    h5. Pre-conditions
      # setup cross compiling enviroment
      # kernel can pass compile normally

	h5. command line
	  # somewhere/collect_cscope_files.py kernel_src_dir kernel_obj_dir
	    #* cscope.files will be genereated in kernel_src_dir

  h3. 2. kernel_pruner.py & make_tags.sh
    h5. Pre-conditions
      # setup cross compiling enviroment
      # make sure kernel can pass compile normally
      # strace should be newer than 4.8, older version could not support mutiple-thread compiling
        #* sudo apt-get remove strace
        #* get it in http://sourceforge.net/projects/strace/
        #* decompress and "./configure && make && sudo make install"
      # *suggest you read make_tags.sh to know what it does, and change it as your special need*

    h5. Run make_tags.sh to generate tags or clean source tree
      # enter kernel dir
      # create cscope.files only
        #* somewhere/make_tags.sh somewhere/kernel_pruner.py your_proj_defconfig
           #** command "ctags -R -L cscope.files && cscope -Rbqk" is called to generate tags
           #** cscope.files will be removed after run "make mrproper", so a backup file cs.files is created
           #** after clean kernel, you can run "cp cs.files cscope.file" and "ctags -R -L cscope.files && cscope -Rbqk"
      # make cscope.files and copy tree:
        #* somewhere/make_tags.sh somewhere/kernel_pruner.py your_proj_defconfig dstdir
      # make cscope.files and link tree:
        #* somewhere/make_tags.sh somewhere/kernel_pruner.py your_proj_defconfig dstdir -l
           #** cscope doesn't support external link file, please refer below link to fix:
                        http://blog.csdn.net/sudolee/article/details/9052291
           #** ctags -R && find -L . | grep -E '\.c$|\.h$|\.S$|\.cpp$|\.lds$' > cscope.files &&  cscope -Rbqk
      # Run kernel_pruner.py directly if strace_log.txt already exists
	#* somewhere/kernel_pruner.py -f strace_log.txt
	#* somewhere/kernel_pruner.py -f strace_log.txt -s . -d anywhere/dstdir
	#* somewhere/kernel_pruner.py -f strace_log.txt -s . -d anywhere/dstdir -l

    h5. verify that the new kernel tree can be compiled normally
      # enter the new kernel dir
      # make mrproper && make your_proj_defconfig &&  make -j8

h1. Verification

Since kernel_pruner.py can make a clean kernel tree that can pass compiling,
so its cscope.files is trustable. Compling cscope.files from 
collect_cscople_file.py to kernel_pruner.py's, you can see a a few redundant .h
files exists, and several .h files missed, but mostly they have no defination 
or unsed in projects.

This slightly difference dosen't harm the symbol searching.
