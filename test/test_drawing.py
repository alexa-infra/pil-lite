import pytest
from PilLite import Image


def test_create():
    img = Image.new(80, 60, 'RGB', 0xff0000)
    assert img.size == (80, 60)


@pytest.fixture(params=[
    dict(fmt='L', color=0xff),
    dict(fmt='L', color=0xa0),
    dict(fmt='L', color=0x0a),
    dict(fmt='LA', color=0xff00),
    dict(fmt='LA', color=0x00ff),
    dict(fmt='RGB', color=0xff0000),
    dict(fmt='RGB', color=0x00ff00),
    dict(fmt='RGB', color=0x0000ff),
    dict(fmt='RGBA', color=0x0000ff00),
    dict(fmt='RGBA', color=0x0000ffff),
    dict(fmt='RGBA', color=0xff00ff00),
    dict(fmt='RGBA', color=0xff00ffff),
])
def color(request):
    yield request.param


def test_create_background(color):
    img = Image.new(80, 60, color['fmt'], color['color'])
    px = img.get_pixel((0, 0))
    assert px == color['color']
    px = img.get_pixel((20, 10))
    assert px == color['color']


def test_draw_rectangle():
    red = 0xff0000
    green = 0x00ff00
    img = Image.new(80, 60, 'RGB', red)
    img.draw_rect((20, 20), (20, 20), green)
    px = img.get_pixel((10, 10))
    assert px == red
    px = img.get_pixel((25, 25))
    assert px == green
