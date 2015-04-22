h1. kernel_pruner.py
Here I'm glad to share you a script, which can generated precise cscope.files and clean kernel tree without redundant files.
It can save your time and patience when searching kernel symbols.

You can get it by
git clone https://github.com/hpyu/kernel_src_pruner.git
or 
\\10.38.198.13\samsung\Users\Haipeng\kernel_pruner\kernel_src_pruner\

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
    h5. Compile kernel with strace
      # generate set_env.sh and compile.sh
        #* python kernel_pruner.py -c

      # change cross compiler path in set_env.sh, change xxx_defconfig file in compile.sh for your requirement
        #* e.g. change pxa1908_defconfig to pxa1936_defconfig

      # compile kernel
        #* source set_env.sh
        #* source compile.sh

      # make sure kernel is compiled successfully, strace_log.txt is the must file needed
      # If strace doesn't support multiple thread compiling, better to install a new vesion
        #* sudo apt-get remove strace
        #* get it in http://sourceforge.net/projects/strace/
        #* decompress and "make && sudo make install"

    h5. Run kernel_pruner.py
      # suppose you are in the original compiled kernel dir
      # create cscope.files only
        #* kernel_pruner.py -f strace_log.txt
           #** cscope.files will be created no matter dst dir is created or not
           #** ctags -R -L cscope.files && cscope -Rbqk

      # make copy tree:
        #* kernel_pruner.py -f strace_log.txt -s . -d  anywhere/k

      # make link tree:
        #* kernel_pruner.py -f strace_log.txt -s . -d  anywhere/k -l
           #** cscope doesn't support external link file, please refer below link to fix:
                        http://blog.csdn.net/sudolee/article/details/9052291
           #** ctags -R && find -L . | grep -E '\.c$|\.h$|\.S$|\.cpp$|\.lds$' > cscope.files &&  cscope -Rbqk
        #* cscope doesn't support link file out of current dir, you can refer below link to fix it
           #** http://blog.csdn.net/sudolee/article/details/9052291
           #** here is compiled one: \\10.38.198.13\samsung\Users\Haipeng\kernel_pruner\cscope

    h5. verify the new kernel tree can be compiled normally
      # enter the new kernel dir
      # source orig_kernel_dir/set_env.sh
      # source orig_kernel_dir/compile.sh

