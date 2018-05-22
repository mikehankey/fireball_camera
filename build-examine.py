#python3 build-examine.py build_ext --inplace
from distutils.core import setup
from Cython.Build import cythonize

setup(
  name = 'examinelib',
  ext_modules = cythonize("examinelib.py"),
)
