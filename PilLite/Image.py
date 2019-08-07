import builtins
import os
import sys
from typing import Optional, Any, Tuple, Union, BinaryIO, cast, TYPE_CHECKING

from PilLiteExt import ffi, lib # pylint: disable=no-name-in-module
if TYPE_CHECKING:
    from PilLiteExt.lib import ImageExt, ImageCompExt


__all__ = ['open']

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


def open(fp: Union[str, BinaryIO], **_kwargs: Any) -> 'Image': # pylint: disable=redefined-builtin
    """
    Opens, reads and decodes the given image file.

    You can use a file object instead of a filename. File object must
    implement ``read`` method, and be opened in binary mode.
    """
    infp = fp
    if not hasattr(fp, 'read'):
        fp = cast(str, fp)
        fp = builtins.open(fp, 'rb')
    fp = cast(BinaryIO, fp)
    if not _is_supported(fp):
        raise IOError('Image open error')
    img = _open_image(fp)
    if infp != fp:
        fp.close()
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

    def save(self, fp: Union[str, BinaryIO], fmt: str = None) -> None:
        """
        Saves this image under the given filename. If no format is
        specified, the format to use is determined from the filename
        extension, if possible.

        You can use a file object instead of a filename. The file object
        must implement the ``write`` method, and be opened in binary mode.
        """
        if not self.im:
            raise ValueError

        infp = fp
        filename = None
        if not hasattr(fp, 'write'):
            filename = cast(str, fp)
            fp = builtins.open(filename, 'wb')
        elif hasattr(fp, 'name'):
            filename = getattr(fp, 'name')
        else:
            filename = ''
        filename = cast(str, filename)
        if not fmt:
            fmt = _guess_format(filename)
        if fmt not in FORMATS:
            raise ValueError("unsupported format %r" % fmt)

        fp = cast(BinaryIO, fp)
        _write_image(self.im, fp, fmt)
        if infp != fp:
            fp.close()

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
