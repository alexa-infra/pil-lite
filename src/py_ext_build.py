import os
from cffi import FFI

THIS_DIR = os.path.dirname(__file__)
STB_DIR = os.path.join(THIS_DIR, 'thirdparty', 'stb')


with open(os.path.join(THIS_DIR, 'lib.h'), 'r') as f:
    ctext = f.read()

ffibuilder = FFI()

ffibuilder.cdef(ctext)

ffibuilder.set_source("_img", """
    #include "lib.h"
""",
    sources=[
        os.path.join(THIS_DIR, 'lib.c'),
        os.path.join(STB_DIR, 'stb_image.c'),
        os.path.join(STB_DIR, 'stb_image_resize.c'),
        os.path.join(STB_DIR, 'stb_image_write.c'),
    ], include_dirs=[THIS_DIR, STB_DIR])

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
