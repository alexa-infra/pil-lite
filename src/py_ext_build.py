from cffi import FFI
ffibuilder = FFI()

with open('lib.h', 'r') as f:
    ctext = f.read()

ffibuilder.cdef(ctext)

ffibuilder.set_source("_img", """
    #include "lib.h"
""",
    sources=[
        'lib.c',
        'thirdparty/stb/stb_image.c',
        'thirdparty/stb/stb_image_resize.c',
        'thirdparty/stb/stb_image_write.c',
    ], include_dirs=['thirdparty/stb/'])

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
