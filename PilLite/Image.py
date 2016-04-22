import os

from PilLiteExt import openImage, writeImageJpeg, writeImagePng

try:
    import builtins
except ImportError:
    import __builtin__
    builtins = __builtin__

def open(fp, mode='r'):
    """
    Opens, reads and decodes the given image file.

    You can use a file object instead of a filename. File object must
    implement ``read`` method, and be opened in binary mode.
    """
    if mode != 'r':
        raise ValueError("bad mode %r" % mode)
    if not hasattr(fp, 'read'):
        filename = fp
        with builtins.open(filename, 'rb') as f:
            img = openImage(f)
    else:
        img = openImage(fp)
    if not img.isOk:
        raise IOError('Image open error: %s' % img.failureReason)
    image = Image()
    image.im = img
    return image

class Image(object):
    def __init__(self):
        self.im = None

    @property
    def size(self):
        """ Returns the size of image, a tuple (width, height) """
        return (self.im.width, self.im.height)

    def save(self, fp, format=None, **kwargs):
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
        ext = os.path.splitext(filename)[1].lower()
        if not format:
            if ext in ['.jpg', '.jpeg']:
                format = 'JPG'
            elif ext in ['.png']:
                format = 'PNG'
            else:
                format = 'PNG'

        if format == 'PNG':
            writeImagePng(self.im, fp)
        elif format == 'JPG':
            writeImageJpeg(self.im, fp)
        else:
            raise ValueError("bad format %r" % format)
        if infp != fp:
            fp.close()

    def resize(self, size):
        """ Returns a resized copy of this image. """
        w, h = size
        image = Image()
        image.im = self.im.resize(w, h)
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
        self.im = self.im.resize(x, y)

