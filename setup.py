#!/usr/bin/python
from distutils.core import Extension, setup
from distutils.command.install import INSTALL_SCHEMES
from Pyrex.Distutils import build_ext
import os

# http://stackoverflow.com/questions/1612733/including-non-python-files-with-setup-py
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

def find_data_files(srcdir, *wildcard):
    file_list = []
    if not srcdir.endswith('/'):
        srcdir+='/'
    for files in os.listdir(srcdir):
        if files.endswith(wildcard):
            file_list.append(srcdir+files)
    return file_list

gfx = find_data_files('data/800x600/gfx/', '.png')
levels = find_data_files('data/800x600/levels/', '.lvl')
music = find_data_files('data/800x600/music/', '.ogg')
snd = find_data_files('data/800x600/snd/', '.wav')

setup( name='MysticMine',
    version='1.0.0',
    author='koonsolo',
    author_email='info@koonsolo.com',
    description='A one switch game',
    url='http://www.koonsolo.com/mysticmine/',
    download_url='http://github.com/koonsolo/MysticMine',
    license='LICENSE.txt',
    scripts=['MysticMine'],
    packages=['monorail','monorail.koon','monorail.tests'],
    data_files=[('monorail/fonts',['monorail/fonts/freesansbold.ttf']),
                ('monorail/data',['data/800x600/edmunds.ttf','data/800x600/font_default.fnt',
                                'data/800x600/font_default.png','data/800x600/resources.cfg',
                               ]
                ),
                ('monorail/data/locale/en_US/LC_MESSAGES/',['data/800x600/locale/en_US/LC_MESSAGES/monorail.mo']),
                ('monorail/data/locale/de_DE/LC_MESSAGES/',['data/800x600/locale/de_DE/LC_MESSAGES/monorail.mo']),
                ('monorail/data/locale/ru_RU/LC_MESSAGES/',['data/800x600/locale/ru_RU/LC_MESSAGES/monorail.mo']),
                ('monorail/data/gfx',gfx),
                ('monorail/data/levels',levels),
                ('monorail/data/music',music),
                ('monorail/data/snd',snd),
    ],
    ext_modules=[
        Extension("monorail.ai", ["monorail/ai.pyx"])
    ],
    cmdclass={'build_ext': build_ext},
    requires=[
        "pygame",
        "numpy",
        "pyrex",
    ],
)
