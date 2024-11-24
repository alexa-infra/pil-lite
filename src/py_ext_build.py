import os
from cffi import FFI

THIS_DIR = os.path.dirname(__file__)
STB_DIR = os.path.join(THIS_DIR, 'stb')


with open(os.path.join(THIS_DIR, 'lib.h'), 'r') as f:
    ctext = f.read()

ffibuilder = FFI()

ffibuilder.cdef(ctext)

ffibuilder.set_source("PilLiteExt", """
    #include "lib.h"
""",
    sources=[
        os.path.join(THIS_DIR, 'lib.c'),
        os.path.join(STB_DIR, 'stb_image.c'),
        os.path.join(STB_DIR, 'stb_image_resize2.c'),
        os.path.join(STB_DIR, 'stb_image_write.c'),
    ],
    include_dirs=[THIS_DIR, STB_DIR],
    define_macros=[
        ('STBI_NO_PSD', None),
        ('STBI_NO_TGA', None),
        ('STBI_NO_GIF', None),
        ('STBI_NO_HDR', None),
        ('STBI_NO_PIC', None),
        ('STBI_NO_PNM', None),
    ])

if __name__ == "__main__":
    ffibuilder.compile()
