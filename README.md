Jutge.org test samples
======================

This small script is intended to be used to check if a program passes the
sample tests for a problem of the online judge [jutge.org](https://jutge.org)
using a diff program.

Features
--------

For the moment it supports automatic download from the
[jutge.org](https://jutge.org) server using the problem code and offline tests
from a custom database.

Installation
------------
The installation process is quite straightforward, simply clone or download
the script `testj.py` and install the dependencies:

```
pip install argparse logging httplib2 bs4
```

Once done, you can execute the program by calling ```python testj.py```

Usage
-----

The most basic usage is to execute the program with the solution of the program
in an executable (meaning either a script or a compiled program). You have
to specify the code of the problem either by including it in the end of your
filename or with the `-c` flag:

```
testj.py myprogram.py -c P00034
testj.py myprogramP00034.o
```
    
You can also provide it a source file and a compiler with its flags. 

```
testj.py myprogram.c --compiler 'gcc' --compiler-flags='-Wall,-g'
```

If the file is ends with `.cpp`, there is no need to specify neither the
compiler nor the flags (defaults to `g++ -g --std=c++11`)

```
testj.py myprogram.c --compiler 'gcc' --compiler-flags='-Wall,-g'
```

By default, the program checks for offline sample input and output files and 
downloads them in `~/Documents/jutge/DB/`, but you can specify another folder
using the `--dir` flag which accepts a comma separated list of directories to
cehck for files, allowing to create additonal tests in another folder.

```
testj.py myprogram.cpp --dir=~/DB/downloaded,~/DB/mytests
```

You can customize the code format using regex with the `--code-regex` flag as 
well as the suffixes of the samples to adapt them to your needs.

See the `testj.py --help` for a list of all the possible options
