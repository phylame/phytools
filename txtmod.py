f#!/usr/bin/env python3
#  Copyright 2014, Peng Wan, <minexiac@gmail.com>
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
from pemx.formats import pmab
from pemx.pio import temp_path
import glob
import zipfile
import os

path = r"E:\books\小说\武侠\云中岳\*.pmab"
output = r"d:\temp"
files = glob.glob(path)
tmpdir = temp_path()

SMART_SPLIT = "ptp --smart-split {0}"
for file in files:
    pkg = zipfile.ZipFile(file)
    title = os.path.splitext(os.path.basename(file))[0]
    out = os.path.join(output, title)
    pkg.extractall(out)
    pkg.close()
    cmd = SMART_SPLIT.format(os.path.normpath('"{0}/Text/*"'.format(out)))
    print(cmd)
    os.system(cmd)
