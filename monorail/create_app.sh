#!/usr/bin/env sh

rm -rf dist build

python setup_py2app.py py2app

svn export ../data/800x600 dist/monorail.app/Contents/Resources/data

mv dist/monorail.app dist/MysticMine.app
mv dist MysticMine

hdiutil create -srcfolder MysticMine mysticmine.dmg
hdiutil internet-enable -yes mysticmine.dmg

mv mysticmine.dmg ../installer/mac/

mv MysticMine dist