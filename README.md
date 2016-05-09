# Installation

`pennsylvaniacao` depends on the GDAL Python package, which in turn
depends on the libgdal20 and libgdal-dev packages.  You need to make
sure that libgdal20 and libgdal-dev are installed and the versions are
the same as those used by the current version of the GDAL Python
package.

Installing pennsylvaniacao will automatically install the GDAL Python
package.  It is necessary to help `pip` figure out where to find the
GDAL library files.

    git clone https://github.com/jhpyle/pennsylvaniacao
    export C_INCLUDE_PATH=/usr/include/gdal
    export CPLUS_INCLUDE_PATH=/usr/include/gdal
    pip install ./pennsylvaniacao
