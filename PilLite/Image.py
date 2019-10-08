import builtins
import os
import sys
from typing import Optional, Any, Tuple, Union, Dict, BinaryIO, cast, TYPE_CHECKING

from PilLiteExt import ffi, lib # pylint: disable=no-name-in-module
if TYPE_CHECKING:
    from PilLiteExt.lib import ImageExt, ImageCompExt


__all__ = ['open', 'new', 'fromarray']

BMP, JPG, PNG = FORMATS = ('bmp', 'jpg', 'png')

EXT_FORMAT = {
    '.jpeg': JPG,
    '.jpg': JPG,
    '.png': PNG,
    '.bmp': BMP,
}

FORMAT_HANDLERS = {
    BMP: lib.image_to_bmp,
    JPG: (lambda img: lib.image_to_jpg(img, 100)),
    PNG: lib.image_to_png,
}

FORMAT_MAGIC = {
    JPG: b'\xFF\xD8\xFF',
    BMP: b'BM',
    PNG: b'\x89PNG',
}


def _guess_format(filename: str) -> Optional[str]:
    _, ext = os.path.splitext(filename)
    ext = ext.lower()
    return EXT_FORMAT.get(ext, None)


def _open_image(fp: BinaryIO) -> 'ImageExt':
    data = ffi.from_buffer('unsigned char[]', fp.read())
    img = lib.image_open(data, len(data))
    rv = ffi.gc(img, lib.image_free, img.width * img.height * img.components)
    if rv.buffer == ffi.NULL:
        raise IOError('Image open error')
    return rv


def _write_image(img: 'ImageExt', fp: BinaryIO, fmt: str) -> None:
    handler = FORMAT_HANDLERS[fmt]
    compressed = handler(img)
    data = ffi.buffer(compressed.buffer, compressed.size)
    fp.write(bytes(data))
    lib.image_compressed_free(compressed)


def _new_image(w: int, h: int, c: int) -> 'ImageExt':
    img = lib.image_new(w, h, c)
    rv = ffi.gc(img, lib.image_free, img.width * img.height * img.components)
    if rv.buffer == ffi.NULL:
        raise IOError('Image create error')
    return rv


def _new_image_raw(data: bytes, w: int, h: int, c: int) -> 'ImageExt':
    buf = ffi.from_buffer('unsigned char[]', data)
    img = lib.image_new_raw(buf, w, h, c)
    rv = ffi.gc(img, lib.image_free, img.width * img.height * img.components)
    if rv.buffer == ffi.NULL:
        raise IOError('Image create error')
    return rv


def open(fp: Union[str, BinaryIO], **_kwargs: Any) -> 'Image': # pylint: disable=redefined-builtin
    """
    Opens, reads and decodes the given image file.

    You can use a file object instead of a filename. File object must
    implement ``read`` method, and be opened in binary mode.
    """
    if isinstance(fp, str):
        fp = builtins.open(fp, 'rb')
        try:
            if not _is_supported(fp):
                raise IOError('Image open error')
            img = _open_image(fp)
        finally:
            fp.close()
    elif hasattr(fp, 'read'):
        if not _is_supported(fp):
            raise IOError('Image open error')
        img = _open_image(fp)
    else:
        raise ValueError
    image = Image()
    image.im = img
    return image


def new(w: int, h: int, fmt: str, bg: int) -> 'Image':
    """
    Creates new image by given size and format
    and fills it with bg color
    """
    if fmt not in ('RGB', 'RGBA', 'L', 'LA'):
        raise ValueError('invalid format')
    c = len(fmt)
    image = Image()
    image.im = _new_image(w, h, c)
    lib.image_draw_rect(image.im, 0, 0, w, h, bg)
    return image


def fromarray(obj: Any) -> 'Image':
    """ Creates new image from numpy array """
    if not hasattr(obj, '__array_interface__'):
        raise ValueError
    if str(obj.dtype) != 'uint8':
        raise ValueError
    shape = obj.shape
    if len(shape) == 2:
        w, h = shape
        components = 1
    elif len(shape) == 3:
        w, h, components = shape
        if components not in (1, 2, 3, 4):
            raise ValueError
    else:
        raise ValueError
    img = _new_image_raw(obj.tobytes(), w, h, components)
    image = Image()
    image.im = img
    return image


class Image:
    im: Optional['ImageExt'] = None

    def __init__(self) -> None:
        self.im = None

    @property
    def size(self) -> Tuple[int, int]:
        """ Returns the size of image, a tuple (width, height) """
        if not self.im:
            raise ValueError
        return (self.im.width, self.im.height)

    def save(self, fp: Union[str, BinaryIO], fmt: Optional[str] = None) -> None:
        """
        Saves this image under the given filename. If no format is
        specified, the format to use is determined from the filename
        extension, if possible.

        You can use a file object instead of a filename. The file object
        must implement the ``write`` method, and be opened in binary mode.
        """
        if not self.im:
            raise ValueError

        if isinstance(fp, str):
            filename = fp
            fp = builtins.open(filename, 'wb')
            try:
                if not fmt:
                    fmt = _guess_format(filename)
                if fmt not in FORMATS:
                    raise ValueError(f'unsupported format {fmt}')
                _write_image(self.im, fp, fmt)
            finally:
                fp.close()
        elif hasattr(fp, 'write'):
            if not fmt and hasattr(fp, 'name'):
                filename = getattr(fp, 'name')
                fmt = _guess_format(filename)
            if fmt not in FORMATS:
                raise ValueError(f'unsupported format {fmt}')
            _write_image(self.im, fp, fmt)
        else:
            raise ValueError

    def resize(self, size: Tuple[int, int]) -> 'Image':
        """ Returns a resized copy of this image. """
        w, h = size
        if not w or not h:
            raise ValueError('invalid size')
        if not self.im:
            raise ValueError
        image = Image()
        resized = lib.image_resize(self.im, w, h)
        image.im = ffi.gc(resized, lib.image_free, w * h * resized.components)
        return image

    def thumbnail(self, size: Tuple[int, int]) -> None:
        """
        Make this image into a thumbnail. This method modifies the
        image to contain a thumbnail version of itself, no larger than
        the given size and preserving original aspect ratio.
        """
        if not self.im:
            raise ValueError
        w, h = size
        x, y = self.size
        if x > w:
            ratio = y / x
            x, y = w, int(ratio * w)
        if y > h:
            ratio = x / y
            x, y = int(ratio * h), h
        resized = self.resize((x, y))
        self.im = resized.im

    def show(self) -> None:
        if not self.im:
            raise ValueError

        from tempfile import NamedTemporaryFile
        from subprocess import run
        with NamedTemporaryFile(suffix='.png') as fp:
            fp = cast(BinaryIO, fp)
            _write_image(self.im, fp, PNG)
            fp.flush()
            if sys.platform == 'linux':
                run(['display', fp.name])

    def put_pixel(self, coord: Tuple[int, int], color: int) -> None:
        """ Draws pixel at (x, y) coord """
        if not self.im:
            raise ValueError
        x, y = coord
        lib.image_put_pixel(self.im, x, y, color)

    def get_pixel(self, coord: Tuple[int, int]) -> int:
        """ Get pixel at (x, y) coord """
        if not self.im:
            raise ValueError
        x, y = coord
        return lib.image_get_pixel(self.im, x, y)

    def draw_rect(self, coord: Tuple[int, int], size: Tuple[int, int], color: int) -> None:
        """ Draws rectagnle at (x, y) coord with (w, h) size"""
        if not self.im:
            raise ValueError
        x, y = coord
        w, h = size
        lib.image_draw_rect(self.im, x, y, w, h, color)

    def tobytes(self) -> bytes:
        """ Raw bytes of image data """
        if not self.im:
            raise ValueError
        size = self.im.width * self.im.height * self.im.components
        return ffi.buffer(self.im.buffer, size)

    @property
    def __array_interface__(self) -> Dict:
        """ Numpy array support """
        if not self.im:
            raise ValueError
        w, h, components = self.im.width, self.im.height, self.im.components
        return {
            'version': 3,
            'shape': (w, h, components),
            'typestr': '|u1',
            'data': self.tobytes(),
        }


def _get_magic_mime(fp: BinaryIO, n: int = 4) -> Optional[bytes]:
    try:
        pos = fp.tell()
        data = fp.read(n)
        if not data or len(data) != n:
            return None
        return data
    except EOFError:
        return None
    finally:
        fp.seek(pos)


def _is_supported(fp: BinaryIO) -> bool:
    buff = _get_magic_mime(fp)
    if not buff:
        return False
    return any(buff.startswith(magic) for magic in FORMAT_MAGIC.values())
