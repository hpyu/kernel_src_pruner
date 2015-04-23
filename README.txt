h1. kernel_pruner.py
This script can generated precise cscope.files and clean kernel tree without redundant files.
It can save your time and patience when searching kernel symbols.

You can get it by
git clone https://github.com/hpyu/kernel_src_pruner.git

*Please send mail to hpyu@marvell.com for any problem when you are using it, I'm willing to improve it with your suggestion.*

  h3. Function
    1. This script pick out only used kernel source files from the whole kernel tree
    2. It can help navigate the kernel source code much more quickly and precisely with ctags&cscope or source insight
    3. It give you a clear view of what source files used in a project

  h3. How it works
    1. Use strace to capture all file accessed when kernel compiling
    2. Parse the strace output file, pick out the used files to build a clean kernel tree and/or generate cscope.files
    3. The new kernel tree can be compiled normally with the defconfig when compiling with strace

  h3. Usage
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
           #** command "ctags -R -L cscope.files && cscope -Rbqk" are called to generate tags
           #** cscope.files will be removed when you run "make mrproper", so a backup file cs.files is created
           #** after clean kernel, you can run "cp cs.files cscope.file" and "ctags -R -L cscope.files && cscope -Rbqk"
      # make cscope.files and copy tree:
        #* somewhere/make_tags.sh somewhere/kernel_pruner.py your_proj_defconfig dstdir
      # make cscope.files and link tree:
        #* somewhere/make_tags.sh somewhere/kernel_pruner.py your_proj_defconfig dstdir -l
           #** cscope doesn't support external link file, please refer below link to fix:
                        http://blog.csdn.net/sudolee/article/details/9052291
           #** ctags -R && find -L . | grep -E '\.c$|\.h$|\.S$|\.cpp$|\.lds$' > cscope.files &&  cscope -Rbqk

    h5. verify that the new kernel tree can be compiled normally
      # enter the new kernel dir
      # make mrproper && make your_proj_defconfig &&  make -j8


