import builtins
import os
import sys

from PilLiteExt import ffi, lib # pylint: disable=no-name-in-module


BMP, JPG, PNG = FORMATS = ('bmp', 'jpg', 'png')

EXT_FORMAT = {
    '.jpeg': JPG,
    '.jpg': JPG,
    '.png': PNG,
    '.bmp': BMP,
}

def _guess_format(filename):
    _, ext = os.path.splitext(filename)
    ext = ext.lower()
    return EXT_FORMAT.get(ext, None)

def _open_image(fp):
    data = ffi.from_buffer('unsigned char[]', fp.read())
    img = lib.image_open(data, len(data))
    rv = ffi.gc(img, lib.image_free, img.width * img.height * img.components)
    if rv.buffer == ffi.NULL:
        err = ffi.string(lib.image_failure_reason())
        raise IOError('Image open error: %s' % err.decode('utf-8'))
    return rv

FORMAT_HANDLERS = {
    BMP: lib.image_to_bmp,
    JPG: (lambda img: lib.image_to_jpg(img, 100)),
    PNG: lib.image_to_png,
}

def _write_image(img, fp, fmt):
    handler = FORMAT_HANDLERS[fmt]
    compressed = handler(img)
    data = ffi.buffer(compressed.buffer, compressed.size)
    fp.write(bytes(data))
    lib.image_compressed_free(compressed)

def open(fp, mode='r'): # pylint: disable=redefined-builtin
    """
    Opens, reads and decodes the given image file.

    You can use a file object instead of a filename. File object must
    implement ``read`` method, and be opened in binary mode.
    """
    infp = fp
    if mode != 'r':
        raise ValueError("bad mode %r" % mode)
    if not hasattr(fp, 'read'):
        fp = builtins.open(fp, 'rb')
    if not is_supported(fp):
        raise IOError('not supported image format')
    img = _open_image(fp)
    if infp != fp:
        fp.close()
    image = Image()
    image.im = img
    return image

class Image:
    def __init__(self):
        self.im = None

    @property
    def size(self):
        """ Returns the size of image, a tuple (width, height) """
        return (self.im.width, self.im.height)

    def save(self, fp, fmt=None):
        """
        Saves this image under the given filename. If no format is
        specified, the format to use is determined from the filename
        extension, if possible.

        You can use a file object instead of a filename. The file object
        must implement the ``write`` method, and be opened in binary mode.
        """
        infp = fp
        filename = None
        if not hasattr(fp, 'write'):
            filename = fp
            fp = builtins.open(filename, 'wb')
        elif hasattr(fp, 'name'):
            filename = fp.name
        else:
            filename = ''
        if not fmt:
            fmt = _guess_format(filename)
        if fmt not in FORMATS:
            raise ValueError("unsupported format %r" % fmt)

        _write_image(self.im, fp, fmt)
        if infp != fp:
            fp.close()

    def resize(self, size):
        """ Returns a resized copy of this image. """
        w, h = size
        image = Image()
        resized = lib.image_resize(self.im, w, h)
        image.im = ffi.gc(resized, lib.image_free, w * h * resized.components)
        return image

    def thumbnail(self, size):
        """
        Make this image into a thumbnail. This method modifies the
        image to contain a thumbnail version of itself, no larger than
        the given size and preserving original aspect ratio.
        """
        w, h = size
        x, y = self.size
        if x > w:
            y = int(max(y * w / x, 1))
            x = int(w)
        if y > h:
            x = int(max(x * h / y, 1))
            y = int(h)
        resized = self.resize((x, y))
        self.im = resized.im

    def show(self):
        from tempfile import NamedTemporaryFile
        from subprocess import run
        with NamedTemporaryFile(suffix='.png') as fp:
            _write_image(self.im, fp, PNG)
            fp.flush()
            if sys.platform == 'linux':
                run(['display', fp.name])

def get_magic_mime(fp):
    try:
        pos = fp.tell()
        data = fp.read(4)
        if not data or len(data) != 4:
            raise EOFError
        return data
    except EOFError:
        return None
    finally:
        fp.seek(pos)

def is_jpeg(buff):
    return buff[:3] == b'\xFF\xD8\xFF'

def is_bmp(buff):
    return buff[:2] == b'BM'

def is_png(buff):
    return buff[:4] == b'\x89PNG'

def is_supported(fp):
    buff = get_magic_mime(fp)
    if not buff:
        return False
    return any(func(buff) for func in (is_jpeg, is_bmp, is_png))
