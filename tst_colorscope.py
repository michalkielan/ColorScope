import unittest
import colorscope
import os
from PIL import Image, ImageDraw
from xvfbwrapper import Xvfb

class Resources:
  def __init__(self):
    size = (10, 10)
    
    self.red = 'red.png'
    self.green = 'green.png'
    self.blue = 'blue.png'
    self.black = 'black.png'
    self.white = 'white.png'
    
    img_red = Image.new('RGB', size, (255, 0 ,0 ))
    img_green = Image.new('RGB', size, (0, 255, 0))
    img_blue = Image.new('RGB', size, (0, 0, 255))
    img_black = Image.new('RGB', size, (0, 0 ,0))
    img_white = Image.new('RGB', size, (255, 255, 255))
    
    img_red.save(self.red)
    img_green.save(self.green)
    img_blue.save(self.blue)
    img_white.save(self.white)
    img_black.save(self.black)
  
  def __del__(self):
    os.remove(self.red)
    os.remove(self.green)
    os.remove(self.blue)
    os.remove(self.black)
    os.remove(self.white)


class ColorReaderRgbMock(colorscope.ColorReaderRGB):
  def read_colors(self, pos):
    return self._read_colors(pos)


class ColorReaderYuvMock(colorscope.ColorReaderYUV):
  def read_colors(self, pos):
    return self._read_colors(pos)


class TestColorscope(unittest.TestCase):
  def setUp(self):
    self.xvfb = Xvfb(width = 1280, height = 720)
    self.addCleanup(self.xvfb.stop)
    self.xvfb.start()
    self.res = Resources()

  def test_factory_create(self):
    colorscope.make_color_reader('rgb', self.res.red)
    colorscope.make_color_reader('yuv', self.res.green)

    with self.assertRaises(AttributeError):
      colorscope.make_color_reader('', '')

    with self.assertRaises(AttributeError):
      colorscope.make_color_reader('invalid', '')

  def test_colorscope_instances(self):
    csRGB = colorscope.ColorReaderRGB(self.res.red)
    csYUV = colorscope.ColorReaderYUV(self.res.green)

    with self.assertRaises(TypeError):
      csINV = colorscope.ColorReader(self.res.red)

  def test_color_red(self):
     img_file = self.res.red
     cr_rgb = ColorReaderRgbMock(img_file)
     cr_yuv = ColorReaderYuvMock(img_file)
     r, g, b = cr_rgb.read_colors((5,5))
     y, u, v = cr_yuv.read_colors((5,5))
     self.assertEqual([r, g, b] , [255, 0, 0])
     self.assertEqual([y, u, v] , [76, 91, 255])

  def test_color_green(self):
     img_file = self.res.green
     cr_rgb = ColorReaderRgbMock(img_file)
     cr_yuv = ColorReaderYuvMock(img_file)
     r, g, b = cr_rgb.read_colors((5,5))
     y, u, v = cr_yuv.read_colors((5,5))
     self.assertEqual([r, g, b] , [0, 255, 0])
     self.assertEqual([y, u, v] , [150, 54, 0])

  def test_color_blue(self):
     img_file = self.res.blue
     cr_rgb = ColorReaderRgbMock(img_file)
     cr_yuv = ColorReaderYuvMock(img_file)
     r, g, b = cr_rgb.read_colors((5,5))
     y, u, v = cr_yuv.read_colors((5,5))
     self.assertEqual([r, g, b] , [0, 0, 255])
     self.assertEqual([y, u, v] , [29, 239, 103])

  def test_color_white(self):
     img_file = self.res.white
     cr_rgb = ColorReaderRgbMock(img_file)
     cr_yuv = ColorReaderYuvMock(img_file)
     r, g, b = cr_rgb.read_colors((5,5))
     y, u, v = cr_yuv.read_colors((5,5))
     self.assertEqual([r, g, b] , [255, 255, 255])
     self.assertEqual([y, u, v] , [255, 128, 128])

  def test_color_black(self):
     img_file = self.res.black
     cr_rgb = ColorReaderRgbMock(img_file)
     cr_yuv = ColorReaderYuvMock(img_file)
     r, g, b = cr_rgb.read_colors((5,5))
     y, u, v = cr_yuv.read_colors((5,5))
     self.assertEqual([r, g, b] , [0, 0, 0])
     self.assertEqual([y, u, v] , [0, 128, 128])


if __name__ == '__main__':
  unittest.main()
