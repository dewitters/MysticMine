#!/usr/bin/env bash

VERSION="1.2.0"
rm -rf dist

rm ai.so
python ./setup.py build_ext --inplace

cxfreeze --include-modules=encodings.ascii,encodings.utf_8 -O -c --target-name=mysticmine monorail.py

cp -R ../data/800x600 dist/data

cp error_mm.log dist
cp quest.stat dist
cp ../LICENSE.txt dist
cp ../assets/graphics/icon48x48.png dist

mv dist mysticmine_${VERSION}

mkdir -p ../installer/linux/
tar zcvf ../installer/linux/mysticmine.tar.gz mysticmine_${VERSION}


mv mysticmine_${VERSION} dist
