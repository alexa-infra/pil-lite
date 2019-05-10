import os
try:
    from tempfile import TemporaryDirectory
except ImportError:
    from backports.tempfile import TemporaryDirectory
import pytest
from PilLite import Image

BASE_DIR = os.path.dirname(__file__)
SIZE = (256, 184)


@pytest.fixture(scope='function')
def tmpdir():
    with TemporaryDirectory() as folder:
        yield folder


@pytest.fixture(params=[
    '.png', '.jpg', '.bmp'
], scope='function')
def infile(request):
    ext = request.param
    yield os.path.join(BASE_DIR, 'data', 'image' + ext)


@pytest.fixture(params=[
    '.png', '.jpg', '.bmp'
], scope='function')
def outfile(tmpdir, request):
    ext = request.param
    yield os.path.join(tmpdir, 'image' + ext)


@pytest.fixture
def png_file():
    yield os.path.join(BASE_DIR, 'data', 'image.png')


@pytest.fixture
def missing_file():
    yield os.path.join(BASE_DIR, 'data', 'missing.png')


@pytest.fixture
def unsupported_file():
    yield os.path.join(BASE_DIR, 'data', 'image.tif')


def test_open(infile):
    img = Image.open(infile)
    assert img.size == SIZE


def test_open_file_desciptor(infile):
    with open(infile, 'rb') as fd:
        img = Image.open(fd)
        assert img.size == SIZE


def test_open_and_save(infile, outfile):
    img = Image.open(infile)
    img.save(outfile)
    assert os.path.exists(outfile)
    img = Image.open(outfile)
    assert img.size == SIZE


def test_open_and_save_file_descriptor(infile, outfile):
    img = Image.open(infile)
    with open(outfile, 'wb') as fd:
        img.save(fd)
    assert os.path.exists(outfile)
    img = Image.open(outfile)
    assert img.size == SIZE


@pytest.fixture(params=[(128, 90), (512, 360)])
def resize(request):
    yield request.param


def test_resize(png_file, resize):
    img = Image.open(png_file)
    img2 = img.resize(resize)
    assert img2 is not img
    assert img2.size == resize
    assert img.size == SIZE


def test_thumbnail(png_file):
    img = Image.open(png_file)
    img.thumbnail((128, 90))
    assert img.size == (125, 90)


def test_not_found(missing_file):
    with pytest.raises(IOError):
        Image.open(missing_file)


def test_unsupported(unsupported_file):
    with pytest.raises(IOError):
        Image.open(unsupported_file)


def test_save_unsupported(png_file, tmpdir):
    img = Image.open(png_file)
    outfile = os.path.join(tmpdir, 'image.tif')
    with pytest.raises(ValueError):
        img.save(outfile)


def test_save_unsupported2(png_file, tmpdir):
    img = Image.open(png_file)
    outfile = os.path.join(tmpdir, 'image')
    with pytest.raises(ValueError):
        img.save(outfile, format='TIFF')
