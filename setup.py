from __future__ import print_function
import glob
import os
import platform as plat
import sys
import fnmatch
from distutils.errors import *
from distutils import log
from distutils import sysconfig

from setuptools import Extension, setup, find_packages
from distutils.command.build_ext import build_ext
from distutils.command.build_clib import build_clib

ARCH = plat.architecture()[0]
ARCH_64 = ARCH in ["x86_64", "64bit"]
WIN32 = sys.platform == 'win32'

def recursive_glob(treeroot, pattern):
    results = []
    for base, dirs, files in os.walk(treeroot):
        goodfiles = fnmatch.filter(files, pattern)
        results.extend(os.path.join(base, f) for f in goodfiles)
    return results

def _read(file):
    with open(file, 'rb') as f:
        return str(f.read())

SRC_PATH = 'src'
THIRDPARTY_PATH = os.path.join(SRC_PATH, 'thirdparty')

STB_PATH = os.path.join(THIRDPARTY_PATH, 'stb')
JPEG_COMPRESSOR_PATH = os.path.join(THIRDPARTY_PATH, 'jpeg-compressor')
BOOST_PYTHON_PATH = os.path.join(THIRDPARTY_PATH, 'boost-python')

MAIN_SRC = glob.glob(os.path.join(SRC_PATH, '*.cpp'))
STB_SRC = glob.glob(os.path.join(STB_PATH, '*.c'))
JPEG_COMPRESSOR_SRC = glob.glob(os.path.join(JPEG_COMPRESSOR_PATH, '*.cpp'))
BOOST_PYTHON_SRC = recursive_glob(os.path.join(BOOST_PYTHON_PATH, 'libs',
                                               'python', 'src'), '*.cpp')

SRC = MAIN_SRC

INC_DIRS = [SRC_PATH, THIRDPARTY_PATH, STB_PATH, JPEG_COMPRESSOR_PATH,
            BOOST_PYTHON_PATH]
DEF_OPTS = [('BOOST_PYTHON_SOURCE', None),
            ('BOOST_MULTI_INDEX_DISABLE_SERIALIZATION', None),
            ('BOOST_PYTHON_STATIC_LIB', None)]
PYVERSION = sys.version[0] + sys.version[2]
LIBS = ['stb', 'jpeg-compressor', 'boost-python']
if WIN32:
    LIBS += ['python' + PYVERSION]

def boost_python_defines(compiler):
    MSVC = compiler == 'msvc'
    MINGW = compiler == 'mingw32'
    defs = []
    if WIN32:
        defs += [('MS_NO_COREDLL', None), ('Py_ENABLE_SHARED', None)]
        if MSVC:
            defs += [('WIN32', None), ('HAVE_ROUND', None)]
        elif ARCH_64:
            defs += [('MS_WIN64', None)]
    return defs

class pil_lite_build_ext(build_ext):
    def build_extensions(self):
        compiler = self.compiler.compiler_type
        MSVC = compiler == 'msvc'
        MINGW = compiler == 'mingw32'
        defs = []
        defs += boost_python_defines(compiler)
        for e in self.extensions:
            e.define_macros += defs
            if MSVC:
                e.extra_compile_args = ['/EHsc']
            if MINGW:
                e.extra_compile_args = ['-Wno-unused-local-typedefs']
        build_ext.build_extensions(self)

class pil_build_clib(build_clib):
    def add_boost_python(self):
        compiler = self.compiler.compiler_type
        MSVC = compiler == 'msvc'
        MINGW = compiler == 'mingw32'
        defs = []
        defs += DEF_OPTS
        defs += boost_python_defines(compiler)
        py_include = sysconfig.get_python_inc()
        plat_py_include = sysconfig.get_python_inc(plat_specific=1)
        inc_dir = [BOOST_PYTHON_PATH, py_include]
        if plat_py_include != py_include:
            inc_dir += [plat_py_include]
        BOOST_PYTHON_CFG = {'sources':BOOST_PYTHON_SRC,
                            'macros':defs,
                            'include_dirs':inc_dir}
        if MSVC:
            BOOST_PYTHON_CFG['extra_compile_args'] = ['/EHsc']
        if MINGW:
            BOOST_PYTHON_CFG['extra_compile_args'] = ['-Wno-unused-local-typedefs']
        BOOST_PYTHON_LIB = ('boost-python', BOOST_PYTHON_CFG)
        self.libraries.append(BOOST_PYTHON_LIB)

    def build_libraries(self, libraries):
        self.add_boost_python()
        for (lib_name, build_info) in libraries:
            sources = build_info.get('sources')
            if sources is None or not isinstance(sources, (list, tuple)):
                raise DistutilsSetupError(
                       "in 'libraries' option (library '%s'), "
                       "'sources' must be present and must be "
                       "a list of source filenames" % lib_name)
            sources = list(sources)

            log.info("building '%s' library", lib_name)

            macros = build_info.get('macros')
            include_dirs = build_info.get('include_dirs')
            extra_args = build_info.get('extra_compile_args', [])
            objects = self.compiler.compile(sources,
                                            output_dir=self.build_temp,
                                            macros=macros,
                                            include_dirs=include_dirs,
                                            extra_postargs=extra_args,
                                            debug=self.debug)

            self.compiler.create_static_lib(objects, lib_name,
                                            output_dir=self.build_clib,
                                            debug=self.debug)

STB_LIB = ('stb', {'sources':STB_SRC})
JPEG_COMPRESSOR_LIB = ('jpeg-compressor', {'sources':JPEG_COMPRESSOR_SRC})

mod = Extension('PilLiteExt', sources=SRC, include_dirs=INC_DIRS,
                define_macros=DEF_OPTS, libraries=LIBS)

NAME = 'Pil-Lite'
PIL_LITE_VERSION = '0.0.3'

setup(name=NAME,
   version=PIL_LITE_VERSION,
   description='Python Imaging Library Lite',
   long_description=_read('README.rst'),
   author='Alexey Vasilyev',
   author_email='alexa.infra@gmail.com',
   license='MIT',
   url = 'https://github.com/alexa-infra/pil-lite',
   download_url = 'https://github.com/alexa-infra/pil-lite/tarball/' + PIL_LITE_VERSION,
   ext_modules=[mod],
   packages=find_packages(),
   libraries=[STB_LIB, JPEG_COMPRESSOR_LIB],
   cmdclass={'build_ext':pil_lite_build_ext, 'build_clib':pil_build_clib},
   zip_safe=True,
   include_package_data=True,
   keywords=["Imaging"],
   platforms='Any',
   classifiers=[
     "Development Status :: 2 - Pre-Alpha",
     "Topic :: Multimedia :: Graphics",
     "Topic :: Multimedia :: Graphics :: Graphics Conversion",
   ],
)
