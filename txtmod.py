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
