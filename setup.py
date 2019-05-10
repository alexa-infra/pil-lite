from __future__ import print_function
import glob
import os
import platform as plat
import sys
from distutils.errors import DistutilsSetupError
from distutils import log
from distutils.command.build_ext import build_ext
from distutils.command.build_clib import build_clib
from setuptools import Extension, setup, find_packages

ARCH = plat.architecture()[0]
ARCH_64 = ARCH in ["x86_64", "64bit"]
WIN32 = sys.platform == 'win32'

def _read(file):
    with open(file, 'rb') as f:
        return f.read().decode('utf-8')

SRC_PATH = 'src'
THIRDPARTY_PATH = os.path.join(SRC_PATH, 'thirdparty')

STB_PATH = os.path.join(THIRDPARTY_PATH, 'stb')

MAIN_SRC = glob.glob(os.path.join(SRC_PATH, '*.cpp'))
STB_SRC = glob.glob(os.path.join(STB_PATH, '*.c'))

SRC = MAIN_SRC

INC_DIRS = [SRC_PATH, THIRDPARTY_PATH, STB_PATH]
DEF_OPTS = [
    ('STBI_NO_PSD',),
    ('STBI_NO_TGA',),
    ('STBI_NO_GIF',),
    ('STBI_NO_HDR',),
    ('STBI_NO_PIC',),
    ('STBI_NO_PNM',),
]
PYVERSION = sys.version[0] + sys.version[2]
LIBS = ['stb']
if WIN32:
    LIBS += ['python' + PYVERSION]

def python_defines(compiler):
    MSVC = compiler == 'msvc'
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
        defs += python_defines(compiler)
        for e in self.extensions:
            e.define_macros += defs
            if MSVC:
                e.extra_compile_args = ['/EHsc']
            if MINGW:
                e.extra_compile_args = ['-Wno-unused-local-typedefs']
        build_ext.build_extensions(self)

class pil_build_clib(build_clib):
    def build_libraries(self, libraries):
        compiler = self.compiler.compiler_type
        GCC = compiler == 'unix'
        MINGW = compiler == 'mingw32'
        for (lib_name, build_info) in libraries:
            sources = build_info.get('sources')
            if sources is None or not isinstance(sources, (list, tuple)):
                raise DistutilsSetupError(
                    "in 'libraries' option (library '%s'), "
                    "'sources' must be present and must be "
                    "a list of source filenames" % lib_name)
            sources = list(sources)

            log.info("building '%s' library", lib_name)

            macros = build_info.get('macros', [])
            macros += [(opt, ) for opt in DEF_OPTS]
            include_dirs = build_info.get('include_dirs')
            extra_args = build_info.get('extra_compile_args', [])
            if GCC or MINGW:
                extra_args.append('-Wno-unused-but-set-variable')
            objects = self.compiler.compile(sources,
                                            output_dir=self.build_temp,
                                            macros=macros,
                                            include_dirs=include_dirs,
                                            extra_preargs=extra_args,
                                            debug=self.debug)

            self.compiler.create_static_lib(objects, lib_name,
                                            output_dir=self.build_clib,
                                            debug=self.debug)

STB_LIB = ('stb', {'sources':STB_SRC})

mod = Extension('PilLiteExt', sources=SRC, include_dirs=INC_DIRS,
                define_macros=DEF_OPTS, libraries=LIBS)

NAME = 'Pil-Lite'
PIL_LITE_VERSION = '0.1.0'

setup(name=NAME,
      version=PIL_LITE_VERSION,
      description='Python Imaging Library Lite',
      long_description=_read('README.rst'),
      author='Alexey Vasilyev',
      author_email='alexa.infra@gmail.com',
      license='MIT',
      url='https://github.com/alexa-infra/pil-lite',
      download_url='https://github.com/alexa-infra/pil-lite/tarball/' + PIL_LITE_VERSION,
      ext_modules=[mod],
      packages=find_packages(),
      libraries=[STB_LIB],
      cmdclass={'build_ext':pil_lite_build_ext, 'build_clib':pil_build_clib},
      zip_safe=True,
      include_package_data=True,
      keywords=["Imaging"],
      platforms='Any',
      classifiers=[
          "Development Status :: 2 - Pre-Alpha",
          "Topic :: Multimedia :: Graphics",
          "Topic :: Multimedia :: Graphics :: Graphics Conversion",
      ])
