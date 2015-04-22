kernel_pruner
=================

## kernel_pruner.py
  * Function
    1. This script pick out only used kernel source files from the whole kernel tree
    2. It can help navigate the kernel source code much more quickly in vi or source insight
    3. It give you a clear view of what source files used in a project

  * How it works
    1. Use strace to capture all file accessed when kernel compiling
    2. Parse the strace output file, pick out the used files to build a clean kernel tree
	3. The new kernel tree can be compiled normally with the defconfig when compiling with strace

  * Usage
    1. Compile kernel with strace
      - generate set_env.sh and compile.sh
        * python kernel_pruner.py -c

      - change cross compiler path in set_env.sh, change xxx_defconfig file in compile.sh
        * e.g. change pxa1908_defconfig to pxa1936_defconfig

      - compile kernel
         * source set_env.sh
         * source compile.sh

      - make sure kernel is compiled successfully, strace_log.txt is the file needed
      - If strace doesn't support multiple thread compiling, better to install a new vesion
        * sudo apt-get remove strace
        * get it in http://sourceforge.net/projects/strace/
        * decompress and "make && sudo make install"

    2. Run kernel_pruner.py
      - suppose you are in the original compiled kernel dir
      - make copy tree:
        * kernel_pruner.py -f strace_log.txt -s . -d  anywhere/k

      - make link tree:
        * kernel_pruner.py -f strace_log.txt -s . -d  anywhere/k -l
		* cscope doesn't support external link file, please refer below link to fix:
			http://blog.csdn.net/sudolee/article/details/9052291
		* time ctags -R && find -L . | grep -E '\.c$|\.h$|\.S$|\.cpp$|\.lds$' > cscope.files &&  time cscope -Rbqk 

      - create cscope.files only
		* kernel_pruner.py -f strace_log.txt
	    * cscope.files will be created no matter dst dir is created or not
		* ctags -R -L cscope.files && cscope -Rbqk

    3. verify the new kernel tree can be compiled normally
      - enter the new kernel dir
      - source orig_kernel_dir/set_env.sh
      - source orig_kernel_dir/compile.sh

