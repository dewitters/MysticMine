# create ai.so with: python setup.py build_ext --inplace

from distutils.core import setup
from distutils.extension import Extension
from Pyrex.Distutils import build_ext
setup(
  name = "AI",
  ext_modules=[
    Extension("ai", ["ai.pyx"], libraries = [])
    ],
  cmdclass = {'build_ext': build_ext}
)
