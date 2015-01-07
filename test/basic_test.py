import os
import shutil
from nose.tools import *

from PilLite import Image

BASE_DIR = os.path.dirname(__file__)
EXTS = ['.png', '.jpg', '.bmp', '.tga'] 
UNSUPPORTED = ['.tif']
SIZE = (256, 184)

class TestBasic:
  def __init__(self):
    self.initial = os.path.join(BASE_DIR, 'data')
    self.temp = os.path.join(BASE_DIR, 'tmp')

  def setUp(self):
    if not os.path.exists(self.temp):
      os.mkdir(self.temp)

  def tearDown(self):
    if os.path.exists(self.temp):
      shutil.rmtree(self.temp)

  def open_and_save(self, in_file, out_file):
    img = Image.open(in_file)
    assert img.size == SIZE
    img.save(out_file)
    assert os.path.exists(out_file)
    img = Image.open(out_file)
    assert img.size == SIZE

  def test_open_and_close(self):
    for ext in EXTS:
      in_file = os.path.join(self.initial, 'image' + ext)
      out_file_png = os.path.join(self.temp, 'image1.png')
      out_file_jpg = os.path.join(self.temp, 'image1.jpg')
      yield self.open_and_save, in_file, out_file_png
      yield self.open_and_save, in_file, out_file_jpg

  @raises(IOError)
  def open_unsupported(self, in_file):
    img = Image.open(in_file)

  def test_open_unsupported(self):
    for ext in UNSUPPORTED:
      in_file = os.path.join(self.initial, 'image' + ext)
      yield self.open_unsupported, in_file     

  def test_open_save_via_file_descriptor(self):
    in_file = os.path.join(self.initial, 'image.png')
    with open(in_file, 'rb') as f:
      img = Image.open(f)
      assert img.size == SIZE
    out_file = os.path.join(self.temp, 'image.png')
    with open(out_file, 'wb') as f:
      img.save(f)
      assert os.path.exists(out_file)
    img = Image.open(out_file)
    assert img.size == SIZE

  def resize(self, new_size):
    in_file = os.path.join(self.initial, 'image.png')
    img = Image.open(in_file)
    img2 = img.resize(new_size)
    assert img2.size == new_size
    out_file = os.path.join(self.temp, 'image.png')
    img2.save(out_file)
    assert os.path.exists(out_file)
    img = Image.open(out_file)
    assert img.size == new_size

  def test_resizes(self):
    sizes = [(128, 90), (512, 360)]
    for s in sizes:
      yield self.resize, s

  def test_thumbnail(self):
    in_file = os.path.join(self.initial, 'image.png')
    img = Image.open(in_file)
    new_size = (128, 90)
    exp_size = (125, 90)
    img.thumbnail(new_size)
    assert img.size == exp_size
    out_file = os.path.join(self.temp, 'image.png')
    img.save(out_file)
    assert os.path.exists(out_file)
    img = Image.open(out_file)
    assert img.size == exp_size

