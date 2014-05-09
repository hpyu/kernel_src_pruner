## Target
----------
    * This tool can make a list of c/h/S files, that is used to setup vim/tags/cscope and SourceInsight project
        1. The core function of this tool is to generate this prefect file list.
        2. The list can be Linux format or Windows format
    * This tool can make a minimal src tree that include only used source files.
        1. It can remove the unused files
        2. It can setup a full symbol link src tree in any other dir
        3. The minimal src tree can be compiled successfully


## Basic Implementation principle
----------
    * Based on a compiled source tree
        1. include/generated/autoconf.h that include all defined CONFIG_xxx
            * This is used to parse #ifdef or #ifndef included .c or .h or .S
        2. all generated .o files to find the corresponding .c and .S

## Detailed Implementation
----------
    1. Copy the src tree to a tmp workplace dir
    2. First level pruning
        * Ignore: Documentation, .git
        * Rremove dirs that have .c/.S but not generated .o except built-in.o
			- to the lowest level dir
			- if no .o, remove this dir
			- if only built-in.o, keep this dir and Makefile, remove src files
    3. .c/.S files to remove
        * init all source files to to_remove_source_list
		* find all .o correspondent .c/.S files, add to compiled_source_list
        * grep the #include "xxx.c" in .c files and #include "xxx.S" in .S
		  add these files to compiled_source_list.
		* remove all compiled_source_list in to_remove_source_list 
	4. .h files
		* init all head files to to_remove_source_list
		* grep all #include <*.h> or "*.h" in compiled_source_list files
		* add the found files to used_source_list
		* remove all head files in used_source_list in to_remove_source_list
	5. Handle the #def related redudent include files










