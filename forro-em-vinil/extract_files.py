#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
from os import listdir
from os.path import isfile, join
import patoolib

unextracted_files = open('unextracted_files.txt', 'w')

for file in [f for f in listdir('/local/datasets/forro/') if isfile(join('/local/datasets/forro/', f))]:
    try:
        patoolib.extract_archive("/local/datasets/forro/%s" % file, outdir="/local/datasets/forro em vinil")
    except:
        unextracted_files.write('%s\n' % file)

unextracted_files.close()
