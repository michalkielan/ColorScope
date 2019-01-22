import unittest
import colorscope
import threading
import os
import cv2

from time import sleep
from pykeyboard import PyKeyboard
from pymouse import PyMouse
from PIL import Image, ImageDraw
from xvfbwrapper import Xvfb


class FakeKeyboard:
  def __init__(self):
    self.__keyboard = PyKeyboard()
  def tap(self, key_code):
    self.__keyboard.tap_key(key_code)
  def tap_esc(self):
    self.tap(9)


class FakeMouse:
  def __init__(self):
    self.__mouse = PyMouse()
  def click(self, x, y):
    self.__mouse.move(x, y)
    self.__mouse.click(x, y)


class Resources:
  def __init__(self):
    size = (10, 10)
    self.rect = [[1,1],[5,5]]
    
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
  def read_rect_color(self, rect):
    return super().read_rect_color(rect)


class ColorReaderYuvMock(colorscope.ColorReaderYUV):
  def read_rect_color(self, pos):
    return super().read_rect_color(pos)


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
      colorscope.make_color_reader('invalid', '')

  def test_colorscope_instances(self):
    csRGB = colorscope.ColorReaderRGB(self.res.red)
    csYUV = colorscope.ColorReaderYUV(self.res.green)

    with self.assertRaises(TypeError):
      csINV = colorscope.ColorReader(self.res.red)

  def test_color_rgb_red(self):
     img_file = self.res.red
     cr_rgb = ColorReaderRgbMock(img_file)
     rgb = cr_rgb.read_rect_color(self.res.rect)
     self.assertEqual(rgb , [255, 0, 0])
  
  def test_color_yuv_red(self):
    img_file = self.res.red
    cr_yuv = ColorReaderYuvMock(img_file)
    yuv = cr_yuv.read_rect_color(self.res.rect)
    self.assertEqual(yuv, [76, 91, 255])
  
  def test_color_filter_median_red(self):
    img_file = self.res.red
    color_filter = colorscope.ColorChannelFilter(cv2.imread(img_file))
    r, g, b = color_filter.median()
    self.assertEqual([b, g, r] , [255, 0, 0])

  def test_color_filter_average_red(self):
    img_file = self.res.red
    color_filter = colorscope.ColorChannelFilter(cv2.imread(img_file))
    r, g, b = color_filter.average()
    self.assertEqual([b, g, r] , [255, 0, 0])

  def test_color_rgb_green(self):
     img_file = self.res.green
     cr_rgb = ColorReaderRgbMock(img_file)
     rgb = cr_rgb.read_rect_color(self.res.rect)
     self.assertEqual(rgb , [0, 255, 0])
  
  def test_color_yuv_green(self):
    img_file = self.res.green
    cr_yuv = ColorReaderYuvMock(img_file)
    yuv = cr_yuv.read_rect_color(self.res.rect)
    self.assertEqual(yuv, [150, 54, 0])
  
  def test_color_filter_median_green(self):
    img_file = self.res.green
    color_filter = colorscope.ColorChannelFilter(cv2.imread(img_file))
    r, g, b = color_filter.median()
    self.assertEqual([b, g, r] , [0, 255, 0])

  def test_color_filter_average_green(self):
    img_file = self.res.green
    color_filter = colorscope.ColorChannelFilter(cv2.imread(img_file))
    r, g, b = color_filter.average()
    self.assertEqual([b, g, r] , [0, 255, 0])

  def test_color_rgb_blue(self):
     img_file = self.res.blue
     cr_rgb = ColorReaderRgbMock(img_file)
     rgb = cr_rgb.read_rect_color(self.res.rect)
     self.assertEqual(rgb , [0, 0, 255])
  
  def test_color_yuv_blue(self):
    img_file = self.res.blue
    cr_yuv = ColorReaderYuvMock(img_file)
    yuv = cr_yuv.read_rect_color(self.res.rect)
    self.assertEqual(yuv, [29, 239, 103])
  
  def test_color_filter_median_blue(self):
    img_file = self.res.blue
    color_filter = colorscope.ColorChannelFilter(cv2.imread(img_file))
    r, g, b = color_filter.median()
    self.assertEqual([b, g, r] , [0, 0, 255])

  def test_color_filter_average_blue(self):
    img_file = self.res.blue
    color_filter = colorscope.ColorChannelFilter(cv2.imread(img_file))
    r, g, b = color_filter.average()
    self.assertEqual([b, g, r] , [0, 0, 255])

  def test_color_rgb_black(self):
     img_file = self.res.black
     cr_rgb = ColorReaderRgbMock(img_file)
     rgb = cr_rgb.read_rect_color(self.res.rect)
     self.assertEqual(rgb , [0, 0, 0])
  
  def test_color_yuv_black(self):
    img_file = self.res.black
    cr_yuv = ColorReaderYuvMock(img_file)
    yuv = cr_yuv.read_rect_color(self.res.rect)
    self.assertEqual(yuv, [0, 128, 128])
  
  def test_color_filter_median_black(self):
    img_file = self.res.black
    color_filter = colorscope.ColorChannelFilter(cv2.imread(img_file))
    r, g, b = color_filter.median()
    self.assertEqual([b, g, r] , [0, 0, 0])

  def test_color_filter_average_black(self):
    img_file = self.res.black
    color_filter = colorscope.ColorChannelFilter(cv2.imread(img_file))
    r, g, b = color_filter.average()
    self.assertEqual([b, g, r] , [0, 0, 0])

  def test_color_rgb_white(self):
     img_file = self.res.white
     cr_rgb = ColorReaderRgbMock(img_file)
     rgb = cr_rgb.read_rect_color(self.res.rect)
     self.assertEqual(rgb , [255, 255, 255])
  
  def test_color_yuv_white(self):
    img_file = self.res.white
    cr_yuv = ColorReaderYuvMock(img_file)
    yuv = cr_yuv.read_rect_color(self.res.rect)
    self.assertEqual(yuv, [255, 128, 128])
  
  def test_color_filter_median_white(self):
    img_file = self.res.white
    color_filter = colorscope.ColorChannelFilter(cv2.imread(img_file))
    r, g, b = color_filter.median()
    self.assertEqual([b, g, r] , [255, 255, 255])

  def test_color_filter_average_white(self):
    img_file = self.res.white
    color_filter = colorscope.ColorChannelFilter(cv2.imread(img_file))
    r, g, b = color_filter.average()
    self.assertEqual([b, g, r] , [255, 255, 255])

  def close_window(self):
    fake_mouse = FakeMouse()
    fake_keyboard = FakeKeyboard()
    start_pos = [50, 50]
    timeout = 3
    x, y = start_pos
    
    sleep(timeout)
    fake_mouse.click(x, y)
    fake_keyboard.tap_esc()

  def test_gui_open_close(self):
    closer = threading.Thread(target=self.close_window)
    closer.start()
    csRGB = colorscope.ColorReaderRGB(self.res.red)
    csRGB.processing()
    closer.join()

  def test_main(self):
     self.assertEqual(0, os.system('python colorscope.py -h'))
     self.assertNotEqual(0, os.system('python colorscope.py -i invalid.png'))
     self.assertNotEqual(0, os.system('python colorscope.py -i red.png -f=invalid'))
     self.assertNotEqual(0, os.system('python colorscope.py -i '))

     self.assertEqual(0, os.system('python colorscope.py --help'))
     self.assertNotEqual(0, os.system('python colorscope.py --imgfile invalid.png'))
     self.assertNotEqual(0, os.system('python colorscope.py --imgfile red.png --format=invalid'))
     self.assertNotEqual(0, os.system('python colorscope.py --imgfile '))


if __name__ == '__main__':
  unittest.main()
