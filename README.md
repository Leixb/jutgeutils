Jutge.org test samples
======================

This small script is intended to be used to check if a program passes the
sample tests for a problem of the online judge [jutge.org](https://jutge.org)
using a diff program.

Features
--------

For the moment it supports automatic download from the
[jutge.org](https://jutge.org) server using the problem code and off-line tests
from a custom database.

Installation
------------
This script uses python3, so you must have it installed in your system. To
install it use your system's package manager.  The installation process is
quite straightforward, simply clone or download the script `testj.py` and
install the dependencies:

```
pip3 install argparse logging httplib2 bs4 httplib2
```

Once done, you can execute the program by calling ```python3 jutge.py```
