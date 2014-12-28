from __future__ import print_function
import glob
import os
import platform as plat
import sys
import fnmatch

from setuptools import Extension, setup, find_packages
from distutils.command.build_ext import build_ext

def recursive_glob(treeroot, pattern):
    results = []
    for base, dirs, files in os.walk(treeroot):
        goodfiles = fnmatch.filter(files, pattern)
        results.extend(os.path.join(base, f) for f in goodfiles)
    return results

SRC_PATH = 'src'
THIRDPARTY_PATH = os.path.join(SRC_PATH, 'thirdparty')

STB_PATH = os.path.join(THIRDPARTY_PATH, 'stb')
JPEG_COMPRESSOR_PATH = os.path.join(THIRDPARTY_PATH, 'jpeg-compressor')
BOOST_PYTHON_PATH = os.path.join(THIRDPARTY_PATH, 'boost-python')

MAIN_SRC = glob.glob(os.path.join(SRC_PATH, '*.cpp'))
STB_SRC = glob.glob(os.path.join(STB_PATH, '*.c'))
JPEG_COMPRESSOR_SRC = glob.glob(os.path.join(JPEG_COMPRESSOR_PATH, '*.cpp'))
BOOST_PYTHON_SRC = recursive_glob(os.path.join(BOOST_PYTHON_PATH, 'libs', 'python', 'src'), '*.cpp')

SRC = MAIN_SRC + STB_SRC + JPEG_COMPRESSOR_SRC + BOOST_PYTHON_SRC

INC_DIRS = [SRC_PATH, THIRDPARTY_PATH, STB_PATH, JPEG_COMPRESSOR_PATH, BOOST_PYTHON_PATH]
DEF_OPTS = [('BOOST_PYTHON_SOURCE', None),
            ('BOOST_MULTI_INDEX_DISABLE_SERIALIZATION', None),
            ('BOOST_PYTHON_STATIC_LIB', None)]
PYVERSION = sys.version[0] + sys.version[2]
LIBS = []
ARCH = plat.architecture()[0]
ARCH_64 = ARCH == '64bit'
WIN32 = sys.platform == 'win32'

if WIN32:
    LIBS += ['python' + PYVERSION]

class pil_lite_build_ext(build_ext):
    def build_extensions(self):
        compiler = self.compiler.compiler_type
        MSVC = compiler == 'msvc'
        MINGW = compiler == 'mingw32'
        defs = []
        if WIN32:
            defs += [('MS_NO_COREDLL', None), ('Py_ENABLE_SHARED', None)]
            if MSVC:
                defs += [('WIN32', None), ('HAVE_ROUND', None)]
            if ARCH_64 and not MSVC:
                defs += [('MS_WIN64', None)]
        for e in self.extensions:
            e.define_macros += defs
            if MSVC:
                e.extra_compile_args = ['/EHsc']
        build_ext.build_extensions(self)

mod = Extension('PilLiteExt', sources=SRC, include_dirs=INC_DIRS, define_macros=DEF_OPTS, libraries=LIBS)

setup(name='PilLite',
   ext_modules=[mod],
   packages=find_packages(),
   cmdclass={'build_ext':pil_lite_build_ext})
