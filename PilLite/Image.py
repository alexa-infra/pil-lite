import os

try:
    from PilLiteExt import openImage, writeImageJpeg, writeImagePng
except ImportError as v:
    raise

try:
    import builtins
except ImportError:
    import __builtin__
    builtins = __builtin__

def open(fp, mode='r'):
    if mode != 'r':
        raise ValueError("bad mode %r" % mode)
    if not hasattr(fp, 'read'):
        filename = fp
        with builtins.open(filename, 'rb') as f:
            img = openImage(f)
    else:
        img = openImage(fp)
    if not img.isOk:
        raise IOError('file %s error: %s' % (filename if filename else fp, img.failureReason))
    image = Image()
    image.im = img
    return image

class Image(object):
    def __init__(self):
        self.im = None

    @property
    def size(self):
        return (self.im.width, self.im.height)

    def save(self, fp, format=None, **kwargs):
        infp = fp
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
        w, h = size
        image = Image()
        image.im = self.im.resize(w, h)
        return image

    def thumbnail(self, size):
        w, h = size
        self.im = self.im.resize(w, h)
