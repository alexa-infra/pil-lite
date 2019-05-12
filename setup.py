import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

def _read(file):
    with open(file, 'rb') as f:
        return f.read().decode('utf-8')

NAME = 'Pil-Lite'
PIL_LITE_VERSION = '0.1.0'
CFFI_DEPENDENCY = 'cffi>=1.1'
CFFI_MODULES = 'src/py_ext_build.py:ffibuilder'
PYTEST_DEPENDENCY = 'pytest'

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

setup(name=NAME,
      version=PIL_LITE_VERSION,
      description='Python Imaging Library Lite',
      long_description=_read('README.rst'),
      author='Alexey Vasilyev',
      author_email='alexa.infra@gmail.com',
      license='MIT',
      url='https://github.com/alexa-infra/pil-lite',
      download_url='https://github.com/alexa-infra/pil-lite/tarball/' + PIL_LITE_VERSION,
      packages=find_packages(),
      python_requires='>=2.7',
      tests_requires=[PYTEST_DEPENDENCY],
      cmdclass={
          'test': PyTest,
      },
      setup_requires=[CFFI_DEPENDENCY],
      install_requires=[CFFI_DEPENDENCY],
      cffi_modules=CFFI_MODULES,
      zip_safe=True,
      include_package_data=True,
      keywords=["Imaging"],
      platforms='Any',
      classifiers=[
          "Development Status :: 2 - Pre-Alpha",
          "Topic :: Multimedia :: Graphics",
          "Topic :: Multimedia :: Graphics :: Graphics Conversion",
      ])
