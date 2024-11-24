from setuptools import setup

setup(packages=["PilLite"],
      cffi_modules=["src/py_ext_build.py:ffibuilder"],
      setup_requires=['cffi>=1.1'])
