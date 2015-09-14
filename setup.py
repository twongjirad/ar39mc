from distutils.core import setup, Extension
from Cython.Build import cythonize
import numpy

import os


# GET ROOT
root_inc_dir = os.popen( 'root-config --incdir' ).readlines()[0].strip()
root_lib_dir = os.popen( 'root-config --libdir' ).readlines()[0].strip()
root_libs = []
ldflags = os.popen( 'root-config --noldflags --libs' ).readlines()[0].split()
for ldflag in ldflags:
    if "-l" in ldflag.strip():
        root_libs.append( ldflag[2:] )
print root_libs
print root_inc_dir
print root_lib_dir

ext_photonlib = Extension( "pyubphotonlib/cyubphotonlib", 
                           ["pyubphotonlib/cyubphotonlib.pyx","pyubphotonlib/PhotonVoxels.cxx","pyubphotonlib/PhotonLibrary.cxx"],
                           library_dirs=[root_lib_dir],
                           libraries=root_libs,
                           language="c++" )

setup(
    name="pyubphotonlib",
    ext_modules=cythonize( [ext_photonlib] ),
    include_dirs=[numpy.get_include(),root_inc_dir],
    packages=["pyubphotonlib"],
)
           
