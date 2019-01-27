import unittest
import threading
import os
import sys
import cv2
import ip.colorreader
import ip.imgloader
import ip.draw
import ip.colorfilter
import colorscope

from time import sleep
from PIL import Image, ImageDraw

def fake_xwindow_supported():
  if sys.platform == 'linux':
    return True
  return False

def is_windows():
  if sys.platform == 'win64' or sys.platform == 'win32':
    return True
  return False

if fake_xwindow_supported():
  from xvfbwrapper import Xvfb
  from pykeyboard import PyKeyboard
  from pymouse import PyMouse

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

    if not is_windows():
      os.system('ffmpeg -y -nostats -loglevel 0 -f rawvideo -video_size 1280x720 -pixel_format nv12 -i /dev/urandom -vframes 1 raw_nv12_1280_720.yuv')
      os.system('ffmpeg -y -nostats -loglevel 0 -f rawvideo -video_size 1280x720 -pixel_format nv21 -i /dev/urandom -vframes 1 raw_nv21_1280_720.yuv')

      os.system('ffmpeg -y -nostats -loglevel 0 -f rawvideo -video_size 1920x1080 -pixel_format nv12 -i /dev/urandom -vframes 1 raw_nv12_1920_1080.yuv')
      os.system('ffmpeg -y -nostats -loglevel 0 -f rawvideo -video_size 1920x1080 -pixel_format nv21 -i /dev/urandom -vframes 1 raw_nv21_1920_1080.yuv')

      self.raw_nv12_1920_1080 = 'raw_nv12_1920_1080.yuv'
      self.raw_nv21_1920_1080 = 'raw_nv21_1920_1080.yuv'

      self.raw_nv12_1280_720 = 'raw_nv12_1280_720.yuv'
      self.raw_nv21_1280_720 = 'raw_nv21_1280_720.yuv'

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


class ColorReaderRgbMock(ip.colorreader.ColorReaderRGB):
  def read_rect_color(self, rect):
    return super().read_rect_color(rect)


class ColorReaderYuvMock(ip.colorreader.ColorReaderYUV):
  def read_rect_color(self, pos):
    return super().read_rect_color(pos)


class ColorReaderHsvMock(ip.colorreader.ColorReaderHSV):
  def read_rect_color(self, pos):
    return super().read_rect_color(pos)


class ColorReaderHlsMock(ip.colorreader.ColorReaderHLS):
  def read_rect_color(self, pos):
    return super().read_rect_color(pos)


class TestColorscope(unittest.TestCase):
  def setUp(self):
    if fake_xwindow_supported():
      self.xvfb = Xvfb(width = 1280, height = 720)
      self.addCleanup(self.xvfb.stop)
      self.xvfb.start()
    self.res = Resources()

  def test_factory_color_read_create(self):
    imloader = ip.imgloader.ImageLoaderDefault(self.res.red)
    ip.colorreader.ColorReader.create('rgb', imloader, 'avg')
    ip.colorreader.ColorReader.create('yuv', imloader, 'avg')
    ip.colorreader.ColorReader.create('hsv', imloader, 'avg')
    ip.colorreader.ColorReader.create('hls', imloader, 'avg')

    with self.assertRaises(AttributeError):
      ip.colorreader.ColorReader.create('', '', '')
      ip.colorreader.ColorReader.create('invalid', '', '')

  def test_colorscope_instances(self):
    imloader = ip.imgloader.ImageLoaderDefault(self.res.red)
    csRGB = ip.colorreader.ColorReaderRGB(imloader)
    csYUV = ip.colorreader.ColorReaderYUV(imloader)
    csHSV = ip.colorreader.ColorReaderHSV(imloader)
    csHLS = ip.colorreader.ColorReaderHLS(imloader)

    with self.assertRaises(TypeError):
      csINV = ip.colorreader.ColorReader(imloader)

  def test_image_loader_factory_nv12(self):
    if not is_windows():
      imloader = ip.imgloader.ImageLoader.create(self.res.raw_nv12_1920_1080, 'nv12', [1920, 1080])
      img = imloader.imread()
      h, w, channels = img.shape
      self.assertEqual([1080, 1920], [h, w])
      self.assertEqual(3, channels)

  def test_image_loader_factory_nv21(self):
    if not is_windows():
      imloader = ip.imgloader.ImageLoader.create(self.res.raw_nv21_1920_1080, 'nv21', [1920, 1080])
      img = imloader.imread()
      h, w, channels = img.shape
      self.assertEqual([1080, 1920], [h, w])
      self.assertEqual(3, channels)

  def test_image_loader_factory_default(self):
    if not is_windows():
      imloader = ip.imgloader.create(self.res.red)
      img = imloader.imread()
      h, w, channels = img.shape
      self.assertEqual([10, 10], [h, w])
      self.assertEqual(3, channels)

  def test_image_loader_factory_failed(self):
    with self.assertRaises(AttributeError):
      imloader = ip.imgloader.ImageLoaderCreate('', 'invalid', [1280, 720])

  def test_image_loader_factory_wrong_size(self):
    if not is_windows():
      with self.assertRaises(ValueError):
        imloader = ip.imgloader.ImageLoader.create(self.res.raw_nv21_1920_1080, 'nv21', [2000, 2000])
        ip.colorreader.ColorReader.create('rgb', imloader, '')

  def test_image_loader_nv12_1080p(self):
    if not is_windows():
      imloader = ip.imgloader.ImageLoaderRawNV12(self.res.raw_nv12_1920_1080, [1920, 1080])
      img = imloader.imread()
      h, w, channels = img.shape
      self.assertEqual([1080, 1920], [h, w])
      self.assertEqual(3, channels)

  def test_image_loader_nv12_720p(self):
    if not is_windows():
      imloader = ip.imgloader.ImageLoaderRawNV12(self.res.raw_nv12_1280_720, [1280, 720])
      img = imloader.imread()
      h, w, channels = img.shape
      self.assertEqual([720, 1280], [h, w])
      self.assertEqual(3, channels)

  def test_image_loader_nv21_1080p(self):
    if not is_windows():
      imloader = ip.imgloader.ImageLoaderRawNV21(self.res.raw_nv21_1920_1080, [1920, 1080])
      img = imloader.imread()
      h, w, channels = img.shape
      self.assertEqual([1080, 1920], [h, w])
      self.assertEqual(3, channels)

  def test_image_loader_nv21_720p(self):
    if not is_windows():
      imloader = ip.imgloader.ImageLoaderRawNV21(self.res.raw_nv21_1280_720, [1280, 720])
      img = imloader.imread()
      h, w, channels = img.shape
      self.assertEqual([720, 1280], [h, w])
      self.assertEqual(3, channels)

  def test_color_rgb_red(self):
    img_file = self.res.red
    img_loader = ip.imgloader.ImageLoaderDefault(img_file)
    cr = ColorReaderRgbMock(img_loader)
    rgb = cr.read_rect_color(self.res.rect)
    self.assertEqual(rgb , [255, 0, 0])

  def test_color_hsv_red(self):
    img_file = self.res.red
    img_loader = ip.imgloader.ImageLoaderDefault(img_file)
    cr = ColorReaderHsvMock(img_loader)
    hsv = cr.read_rect_color(self.res.rect)
    self.assertEqual(hsv , [0, 255, 255])

  def test_color_hls_red(self):
    img_file = self.res.red
    img_loader = ip.imgloader.ImageLoaderDefault(img_file)
    cr = ColorReaderHlsMock(img_loader)
    hls = cr.read_rect_color(self.res.rect)
    self.assertEqual(hls , [0, 128, 255])

  def test_color_yuv_red(self):
    img_file = self.res.red
    img_loader = ip.imgloader.ImageLoaderDefault(img_file)
    cr = ColorReaderYuvMock(img_loader)
    yuv = cr.read_rect_color(self.res.rect)
    self.assertEqual(yuv, [76, 91, 255])

  def test_color_filter_median_red(self):
    img_file = self.res.red
    color_filter = ip.colorfilter.ColorChannelFilterMedian()
    r, g, b = color_filter.filter(cv2.imread(img_file))
    self.assertEqual([b, g, r] , [255, 0, 0])

  def test_color_filter_average_red(self):
    img_file = self.res.red
    color_filter = ip.colorfilter.ColorChannelFilterAverage()
    r, g, b = color_filter.filter(cv2.imread(img_file))
    self.assertEqual([b, g, r] , [255, 0, 0])

  def test_color_rgb_green(self):
     img_file = self.res.green
     img_loader = ip.imgloader.ImageLoaderDefault(img_file)
     cr = ColorReaderRgbMock(img_loader)
     rgb = cr.read_rect_color(self.res.rect)
     self.assertEqual(rgb , [0, 255, 0])

  def test_color_hsv_green(self):
     img_file = self.res.green
     img_loader = ip.imgloader.ImageLoaderDefault(img_file)
     cr = ColorReaderHsvMock(img_loader)
     hsv = cr.read_rect_color(self.res.rect)
     self.assertEqual(hsv , [60, 255, 255])

  def test_color_hls_green(self):
     img_file = self.res.green
     img_loader = ip.imgloader.ImageLoaderDefault(img_file)
     cr = ColorReaderHlsMock(img_loader)
     hls = cr.read_rect_color(self.res.rect)
     self.assertEqual(hls , [60, 128, 255])

  def test_color_yuv_green(self):
    img_file = self.res.green
    img_loader = ip.imgloader.ImageLoaderDefault(img_file)
    cr = ColorReaderYuvMock(img_loader)
    yuv = cr.read_rect_color(self.res.rect)
    self.assertEqual(yuv, [150, 54, 0])

  def test_color_filter_median_green(self):
    img_file = self.res.green
    color_filter = ip.colorfilter.ColorChannelFilterMedian()
    r, g, b = color_filter.filter(cv2.imread(img_file))
    self.assertEqual([b, g, r] , [0, 255, 0])

  def test_color_filter_average_green(self):
    img_file = self.res.green
    color_filter = ip.colorfilter.ColorChannelFilterAverage()
    r, g, b = color_filter.filter(cv2.imread(img_file))
    self.assertEqual([b, g, r] , [0, 255, 0])

  def test_color_rgb_blue(self):
     img_file = self.res.blue
     img_loader = ip.imgloader.ImageLoaderDefault(img_file)
     cr = ColorReaderRgbMock(img_loader)
     rgb = cr.read_rect_color(self.res.rect)
     self.assertEqual(rgb , [0, 0, 255])

  def test_color_hsv_blue(self):
     img_file = self.res.blue
     img_loader = ip.imgloader.ImageLoaderDefault(img_file)
     cr = ColorReaderHsvMock(img_loader)
     hsv = cr.read_rect_color(self.res.rect)
     self.assertEqual(hsv , [120, 255, 255])

  def test_color_hls_blue(self):
     img_file = self.res.blue
     img_loader = ip.imgloader.ImageLoaderDefault(img_file)
     cr = ColorReaderHlsMock(img_loader)
     hls = cr.read_rect_color(self.res.rect)
     self.assertEqual(hls, [120, 128, 255])

  def test_color_yuv_blue(self):
    img_file = self.res.blue
    img_loader = ip.imgloader.ImageLoaderDefault(img_file)
    cr = ColorReaderYuvMock(img_loader)
    yuv = cr.read_rect_color(self.res.rect)
    self.assertEqual(yuv, [29, 239, 103])

  def test_color_filter_median_blue(self):
    img_file = self.res.blue
    color_filter = ip.colorfilter.ColorChannelFilterMedian()
    r, g, b = color_filter.filter(cv2.imread(img_file))
    self.assertEqual([b, g, r] , [0, 0, 255])

  def test_color_filter_average_blue(self):
    img_file = self.res.blue
    color_filter = ip.colorfilter.ColorChannelFilterAverage()
    r, g, b = color_filter.filter(cv2.imread(img_file))
    self.assertEqual([b, g, r] , [0, 0, 255])

  def test_color_rgb_black(self):
     img_file = self.res.black
     img_loader = ip.imgloader.ImageLoaderDefault(img_file)
     cr = ColorReaderRgbMock(img_loader)
     rgb = cr.read_rect_color(self.res.rect)
     self.assertEqual(rgb , [0, 0, 0])

  def test_color_hsv_black(self):
     img_file = self.res.black
     img_loader = ip.imgloader.ImageLoaderDefault(img_file)
     cr = ColorReaderHsvMock(img_loader)
     hsv = cr.read_rect_color(self.res.rect)
     self.assertEqual(hsv , [0, 0, 0])

  def test_color_hls_black(self):
     img_file = self.res.black
     img_loader = ip.imgloader.ImageLoaderDefault(img_file)
     cr = ColorReaderHlsMock(img_loader)
     hls = cr.read_rect_color(self.res.rect)
     self.assertEqual(hls , [0, 0, 0])

  def test_color_yuv_black(self):
    img_file = self.res.black
    img_loader = ip.imgloader.ImageLoaderDefault(img_file)
    cr = ColorReaderYuvMock(img_loader)
    yuv = cr.read_rect_color(self.res.rect)
    self.assertEqual(yuv, [0, 128, 128])

  def test_color_filter_median_black(self):
    img_file = self.res.black
    color_filter = ip.colorfilter.ColorChannelFilterMedian()
    r, g, b = color_filter.filter(cv2.imread(img_file))
    self.assertEqual([b, g, r] , [0, 0, 0])

  def test_color_filter_average_black(self):
    img_file = self.res.black
    color_filter = ip.colorfilter.ColorChannelFilterAverage()
    r, g, b = color_filter.filter(cv2.imread(img_file))
    self.assertEqual([b, g, r] , [0, 0, 0])

  def test_color_rgb_white(self):
     img_file = self.res.white
     img_loader = ip.imgloader.ImageLoaderDefault(img_file)
     cr = ColorReaderRgbMock(img_loader)
     rgb = cr.read_rect_color(self.res.rect)
     self.assertEqual(rgb , [255, 255, 255])

  def test_color_hsv_white(self):
     img_file = self.res.white
     img_loader = ip.imgloader.ImageLoaderDefault(img_file)
     cr = ColorReaderHsvMock(img_loader)
     hsv = cr.read_rect_color(self.res.rect)
     self.assertEqual(hsv, [0, 0, 255])

  def test_color_hls_white(self):
     img_file = self.res.white
     img_loader = ip.imgloader.ImageLoaderDefault(img_file)
     cr = ColorReaderHlsMock(img_loader)
     hls = cr.read_rect_color(self.res.rect)
     self.assertEqual(hls, [0, 255, 0])

  def test_color_yuv_white(self):
    img_file = self.res.white
    img_loader = ip.imgloader.ImageLoaderDefault(img_file)
    cr = ColorReaderYuvMock(img_loader)
    yuv = cr.read_rect_color(self.res.rect)
    self.assertEqual(yuv, [255, 128, 128])

  def test_color_filter_median_white(self):
    img_file = self.res.white
    color_filter = ip.colorfilter.ColorChannelFilterMedian()
    r, g, b = color_filter.filter(cv2.imread(img_file))
    self.assertEqual([b, g, r] , [255, 255, 255])

  def test_color_filter_average_white(self):
    img_file = self.res.white
    color_filter = ip.colorfilter.ColorChannelFilterAverage()
    r, g, b = color_filter.filter(cv2.imread(img_file))
    self.assertEqual([b, g, r] , [255, 255, 255])

  def close_window(self):
    if fake_xwindow_supported():
      fake_mouse = FakeMouse()
      fake_keyboard = FakeKeyboard()
      start_pos = [50, 50]
      timeout = 3
      x, y = start_pos

      sleep(timeout)
      fake_mouse.click(x, y)
      fake_keyboard.tap_esc()

  def test_gui_open_close(self):
    if fake_xwindow_supported():
      closer = threading.Thread(target=self.close_window)
      closer.start()
      image_loader = ip.imgloader.ImageLoaderDefault(self.res.red)
      csRGB = ip.colorreader.ColorReaderRGB(image_loader)
      csRGB.processing()
      closer.join()

  def test_main(self):
    exe = ''
    if is_windows():
      exe = '%PYTHON%\\python.exe '
    else:
      exe = 'python '
    self.assertEqual(0, os.system(exe + ' colorscope.py -h'))
    self.assertNotEqual(0, os.system(exe + ' colorscope.py -i invalid.png'))
    self.assertNotEqual(0, os.system(exe + ' colorscope.py -i red.png -out_fmt=invalid'))
    self.assertNotEqual(0, os.system(exe + ' colorscope.py -i '))

    self.assertEqual(0, os.system(exe + ' colorscope.py --help'))
    self.assertNotEqual(0, os.system(exe + ' colorscope.py --imgfile invalid.png'))
    self.assertNotEqual(0, os.system(exe + ' colorscope.py --imgfile red.png --output_format=invalid'))
    self.assertNotEqual(0, os.system(exe + ' colorscope.py --imgfile '))


if __name__ == '__main__':
  unittest.main()
