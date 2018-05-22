#python3 build-cython.py build_ext --inplace
from distutils.core import setup
from Cython.Build import cythonize

setup(
  name = 'stack_loop',
  ext_modules = cythonize("stack_loop.py"),
)
