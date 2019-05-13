import io
import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand


about = {}
with open('PilLite/__about__.py') as fp:
    exec(fp.read(), about)


CFFI_DEPENDENCY = 'cffi>=1.1'
CFFI_MODULES = 'src/py_ext_build.py:ffibuilder'
PYTEST_DEPENDENCY = 'pytest'
CLASSIFIERS = """
    Development Status :: 4 - Beta
    License :: OSI Approved :: MIT License
    Programming Language :: Python :: Implementation :: CPython
    Programming Language :: Python :: Implementation :: PyPy
    Programming Language :: Python :: 2
    Programming Language :: Python :: 3
    Topic :: Utilities
    Topic :: Multimedia :: Graphics
    Topic :: Multimedia :: Graphics :: Graphics Conversion
"""
CLASSIFIERS_LIST = [c.strip() for c in CLASSIFIERS.split('\n') if c]


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(name=about['__title__'],
      version=about['__version__'],
      description=about['__summary__'],
      long_description=io.open('README.rst', encoding='utf-8').read(),
      author=about['__author__'],
      author_email=about['__email__'],
      license=about['__license__'],
      url=about['__uri__'],
      download_url='{}/tarball/{}'.format(about['__uri__'], about['__version__']),
      packages=[
          'PilLite',
      ],
      python_requires='>=2.7',
      tests_require=[PYTEST_DEPENDENCY],
      cmdclass={
          'test': PyTest,
      },
      setup_requires=[CFFI_DEPENDENCY],
      install_requires=[CFFI_DEPENDENCY],
      cffi_modules=CFFI_MODULES,
      zip_safe=False,
      keywords=['Imaging'],
      platforms='Any',
      classifiers=CLASSIFIERS_LIST)
