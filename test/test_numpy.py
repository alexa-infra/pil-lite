import pytest

try:
    import numpy as np
except ImportError:
    pytest.skip('Numpy is not installed', allow_module_level=True)

from PilLite import Image


def test_to_array():
    img = Image.open('test/data/image.png')
    im = np.array(img)
    assert im.ndim == 3
    assert im.dtype == np.dtype('uint8')


def test_to_array_color():
    img = Image.new(10, 10, 'RGB', 0xff0000)
    im = np.array(img)
    assert im.ndim == 3
    assert im.dtype == np.dtype('uint8')
    pixel = np.array([255, 0, 0], 'u1')
    np.testing.assert_array_equal(im[0, 0], pixel)
    arr = np.tile(pixel, 10 * 10).reshape((10, 10, 3))
    np.testing.assert_array_equal(im, arr)


def test_from_array():
    pixel = np.array([255, 0, 0], 'u1')
    arr = np.tile(pixel, 10 * 10).reshape((10, 10, 3))
    img = Image.fromarray(arr)
    assert img.size == (10, 10)
    arr_back = np.array(img)
    np.testing.assert_array_equal(arr, arr_back)
