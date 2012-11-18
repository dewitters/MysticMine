#!/usr/bin/env bash

rm -rf dist

cxfreeze --include-modules=encodings.ascii,encodings.utf_8 -O -c --target-name=mysticmine monorail.py

svn export ../data/800x600 dist/data

cp error_mm.log dist
cp quest.stat dist
cp ../../../koonsolo/eula/LICENSE dist
cp ../assets/graphics/icon48x48.png dist

mv dist mysticmine_1.2.0
tar zcvf ../installer/linux/mysticmine.tar.gz mysticmine_1.2.0


mv mysticmine_1.2.0 dist
