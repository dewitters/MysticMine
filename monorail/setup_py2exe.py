from distutils.core import setup
import py2exe

setup(windows=[ {"script" : 'monorail.py',
                 "icon_resources": [(1, "icon.ico")]
                }])

# run as: python setup_py2exe.py py2exe
