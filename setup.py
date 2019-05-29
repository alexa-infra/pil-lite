import io
import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand


about = {}
with io.open('PilLite/__about__.py', encoding='utf-8') as fp:
    exec(fp.read(), about)
about = {
    k.strip('_'): v for k, v in about.items() if k not in ('__builtins__', '__all__')}
with io.open('README.rst', encoding='utf-8') as fp:
    readme = fp.read()


CFFI_DEPENDENCY = 'cffi>=1.1'
CFFI_MODULES = 'src/py_ext_build.py:ffibuilder'
PYTEST_DEPENDENCY = 'pytest'
CLASSIFIERS = """
    Development Status :: 4 - Beta
    License :: OSI Approved :: MIT License
    Programming Language :: Python :: Implementation :: CPython
    Programming Language :: Python :: Implementation :: PyPy
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


setup(name=about['title'],
      version=about['version'],
      description=about['summary'],
      long_description=readme,
      author=about['author'],
      author_email=about['email'],
      license=about['license'],
      url=about['uri'],
      download_url='{}/tarball/{}'.format(about['uri'], about['version']),
      packages=[
          'PilLite',
      ],
      python_requires='>=3',
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
