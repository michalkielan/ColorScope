import unittest
import threading
import os
import sys
import cv2
import matplotlib.pyplot as plt
import ip.colorreader
import ip.imgloader
import ip.draw
import ip.colorfilter
import ip.colorjson
import ip.graph
import colorscope

from time import sleep
from PIL import Image, ImageDraw

def fake_xwindow_supported():
  if sys.platform == 'linux':
    return True
  return False

if fake_xwindow_supported():
  from xvfbwrapper import Xvfb
  from pykeyboard import PyKeyboard
  from pymouse import PyMouse

def is_windows():
  if sys.platform == 'win64' or sys.platform == 'win32':
    return True
  return False

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
    self.res = Resources()

  def make_fake_display(self, size):
    if fake_xwindow_supported():
      fake_display = Xvfb(width = 1280, height = 720)
      return fake_display
    raise IOError('Fake xwindow not supported')

  def test_const(self):
    self.assertEqual(ip.graph.Const.get_max_hue(), 179)
    self.assertEqual(ip.graph.Const.get_max_saturation(), 255)
    self.assertEqual(ip.graph.Const.get_max_lightness(), 255)
    self.assertEqual(ip.graph.Const.Symbols.delta(), '\u0394')

  def test_factory_color_read_create(self):
    imloader = ip.imgloader.ImageLoaderDefault(self.res.red)
    ip.colorreader.ColorReader.create('rgb', imloader, 'avg', 'test.json')
    ip.colorreader.ColorReader.create('yuv', imloader, 'avg', 'test.json')
    ip.colorreader.ColorReader.create('hsv', imloader, 'avg', 'test.json')
    ip.colorreader.ColorReader.create('hls', imloader, 'avg', 'test.json')

    with self.assertRaises(AttributeError):
      ip.colorreader.ColorReader.create('', '', '', '')
      ip.colorreader.ColorReader.create('invalid', '', '', '')

  def test_colorscope_instances(self):
    imloader = ip.imgloader.ImageLoaderDefault(self.res.red)
    csRGB = ip.colorreader.ColorReaderRGB(imloader, 'test.json')
    csYUV = ip.colorreader.ColorReaderYUV(imloader, 'test.json')
    csHSV = ip.colorreader.ColorReaderHSV(imloader, 'test.json')
    csHLS = ip.colorreader.ColorReaderHLS(imloader, 'test.json')

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
        imloader = ip.imgloader.ImageLoader.create(
                       self.res.raw_nv21_1920_1080,
                       'nv21',
                       [2000, 2000]
        )
        ip.colorreader.ColorReader.create('rgb', imloader, '', '')

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
    cr = ColorReaderRgbMock(img_loader, 'test.json')
    rgb = cr.read_rect_color(self.res.rect)
    self.assertEqual(rgb , [255, 0, 0])

  def test_color_hsv_red(self):
    img_file = self.res.red
    img_loader = ip.imgloader.ImageLoaderDefault(img_file)
    cr = ColorReaderHsvMock(img_loader, 'test.json')
    hsv = cr.read_rect_color(self.res.rect)
    self.assertEqual(hsv , [0, 255, 255])

  def test_color_hls_red(self):
    img_file = self.res.red
    img_loader = ip.imgloader.ImageLoaderDefault(img_file)
    cr = ColorReaderHlsMock(img_loader, 'test.json')
    hls = cr.read_rect_color(self.res.rect)
    self.assertEqual(hls , [0, 128, 255])

  def test_color_yuv_red(self):
    img_file = self.res.red
    img_loader = ip.imgloader.ImageLoaderDefault(img_file)
    cr = ColorReaderYuvMock(img_loader, 'test.json')
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
     cr = ColorReaderRgbMock(img_loader, 'test.json')
     rgb = cr.read_rect_color(self.res.rect)
     self.assertEqual(rgb , [0, 255, 0])

  def test_color_hsv_green(self):
     img_file = self.res.green
     img_loader = ip.imgloader.ImageLoaderDefault(img_file)
     cr = ColorReaderHsvMock(img_loader, 'test.json')
     hsv = cr.read_rect_color(self.res.rect)
     self.assertEqual(hsv , [60, 255, 255])

  def test_color_hls_green(self):
     img_file = self.res.green
     img_loader = ip.imgloader.ImageLoaderDefault(img_file)
     cr = ColorReaderHlsMock(img_loader, 'test.json')
     hls = cr.read_rect_color(self.res.rect)
     self.assertEqual(hls , [60, 128, 255])

  def test_color_yuv_green(self):
    img_file = self.res.green
    img_loader = ip.imgloader.ImageLoaderDefault(img_file)
    cr = ColorReaderYuvMock(img_loader, 'test.json')
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
     cr = ColorReaderRgbMock(img_loader, 'test.json')
     rgb = cr.read_rect_color(self.res.rect)
     self.assertEqual(rgb , [0, 0, 255])

  def test_color_hsv_blue(self):
     img_file = self.res.blue
     img_loader = ip.imgloader.ImageLoaderDefault(img_file)
     cr = ColorReaderHsvMock(img_loader, 'test.json')
     hsv = cr.read_rect_color(self.res.rect)
     self.assertEqual(hsv , [120, 255, 255])

  def test_color_hls_blue(self):
     img_file = self.res.blue
     img_loader = ip.imgloader.ImageLoaderDefault(img_file)
     cr = ColorReaderHlsMock(img_loader, 'test.json')
     hls = cr.read_rect_color(self.res.rect)
     self.assertEqual(hls, [120, 128, 255])

  def test_color_yuv_blue(self):
    img_file = self.res.blue
    img_loader = ip.imgloader.ImageLoaderDefault(img_file)
    cr = ColorReaderYuvMock(img_loader, 'test.json')
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
     cr = ColorReaderRgbMock(img_loader, 'test.json')
     rgb = cr.read_rect_color(self.res.rect)
     self.assertEqual(rgb , [0, 0, 0])

  def test_color_hsv_black(self):
     img_file = self.res.black
     img_loader = ip.imgloader.ImageLoaderDefault(img_file)
     cr = ColorReaderHsvMock(img_loader, 'test.json')
     hsv = cr.read_rect_color(self.res.rect)
     self.assertEqual(hsv , [0, 0, 0])

  def test_color_hls_black(self):
     img_file = self.res.black
     img_loader = ip.imgloader.ImageLoaderDefault(img_file)
     cr = ColorReaderHlsMock(img_loader, 'test.json')
     hls = cr.read_rect_color(self.res.rect)
     self.assertEqual(hls , [0, 0, 0])

  def test_color_yuv_black(self):
    img_file = self.res.black
    img_loader = ip.imgloader.ImageLoaderDefault(img_file)
    cr = ColorReaderYuvMock(img_loader, 'test.json')
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
     cr = ColorReaderRgbMock(img_loader, 'test.json')
     rgb = cr.read_rect_color(self.res.rect)
     self.assertEqual(rgb , [255, 255, 255])

  def test_color_hsv_white(self):
     img_file = self.res.white
     img_loader = ip.imgloader.ImageLoaderDefault(img_file)
     cr = ColorReaderHsvMock(img_loader, 'test.json')
     hsv = cr.read_rect_color(self.res.rect)
     self.assertEqual(hsv, [0, 0, 255])

  def test_color_hls_white(self):
     img_file = self.res.white
     img_loader = ip.imgloader.ImageLoaderDefault(img_file)
     cr = ColorReaderHlsMock(img_loader, 'test.json')
     hls = cr.read_rect_color(self.res.rect)
     self.assertEqual(hls, [0, 255, 0])

  def test_color_yuv_white(self):
    img_file = self.res.white
    img_loader = ip.imgloader.ImageLoaderDefault(img_file)
    cr = ColorReaderYuvMock(img_loader, 'test.json')
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

  def test_json_rgb(self):
    json_filename = 'rgb_json.json'
    cj = ip.colorjson.JsonSerializerRGB(json_filename)
    cj.append([254, 219, 21])
    cj.append([237, 254, 51])
    cj.append([254, 250, 168])
    cj.write()

    cjp = ip.colorjson.JsonDeserializer(json_filename)
    self.assertEqual('rgb', cjp.get()['format'])
    self.assertEqual([254, 237, 254], cjp.get()['channels']['r'])
    self.assertEqual([219, 254, 250], cjp.get()['channels']['g'])
    self.assertEqual([21, 51, 168], cjp.get()['channels']['b'])
    os.remove(json_filename)

  def test_json_yuv(self):
    json_filename = 'yuv_json.json'
    cj = ip.colorjson.JsonSerializerYUV(json_filename)
    cj.append([0, 128, 128])
    cj.append([185, 82, 188])
    cj.append([248, 114, 133])
    cj.write()

    cjp = ip.colorjson.JsonDeserializer(json_filename)
    self.assertEqual('yuv', cjp.get()['format'])
    self.assertEqual([0, 185, 248], cjp.get()['channels']['y'])
    self.assertEqual([128, 82, 114], cjp.get()['channels']['u'])
    self.assertEqual([128, 188, 133], cjp.get()['channels']['v'])
    os.remove(json_filename)

  def test_json_hsv(self):
    json_filename = 'hsv_json.json'
    cj = ip.colorjson.JsonSerializerHSV(json_filename)
    cj.append([24, 227, 255])
    cj.append([1, 217, 254])
    cj.append([112, 145, 254])
    cj.write()

    cjp = ip.colorjson.JsonDeserializer(json_filename)
    self.assertEqual('hsv', cjp.get()['format'])
    self.assertEqual([24, 1, 112], cjp.get()['channels']['h'])
    self.assertEqual([227, 217, 145], cjp.get()['channels']['s'])
    self.assertEqual([255, 254, 254], cjp.get()['channels']['v'])
    os.remove(json_filename)

  def test_json_hls(self):
    json_filename = 'hls_json.json'
    cj = ip.colorjson.JsonSerializerHLS(json_filename)
    cj.append([9, 155, 237])
    cj.append([61, 234, 253])
    cj.append([150, 166, 254])
    cj.write()

    cjp = ip.colorjson.JsonDeserializer(json_filename)
    self.assertEqual('hls', cjp.get()['format'])
    self.assertEqual([9, 61, 150], cjp.get()['channels']['h'])
    self.assertEqual([155, 234, 166], cjp.get()['channels']['l'])
    self.assertEqual([237, 253, 254], cjp.get()['channels']['s'])
    os.remove(json_filename)

  def test_colormeter(self):
    ref_filename = 'color_meter_tests_ref_json.json'
    ref_cj = ip.colorjson.JsonSerializerHLS(ref_filename)
    ref_cj.append([10, 10, 10])
    ref_cj.append([10, 10, 10])
    ref_cj.append([10, 10, 10])
    ref_cj.write()

    cap_filename = 'color_meter_tests_cap_json.json'
    cap_cj = ip.colorjson.JsonSerializerHLS(cap_filename)
    cap_cj.append([20, 20, 20])
    cap_cj.append([20, 20, 20])
    cap_cj.append([20, 20, 20])
    cap_cj.write()

    ref_js = ip.colorjson.JsonDeserializer(ref_filename)
    cap_js = ip.colorjson.JsonDeserializer(cap_filename)

    color_meter = ip.colormeter.ColorMeter(ref_js, cap_js)
    avg_h, avg_l, avg_s = color_meter.get_hls_delta_perc()

    self.assertEqual(200, avg_h)
    self.assertEqual(200, avg_l)
    self.assertEqual(200, avg_s)

    os.remove(ref_filename)
    os.remove(cap_filename)

  def test_colormeter_failed(self):
    ref_yuv_filename = 'color_meter_failed_yuv_ref_json.json'
    cap_yuv_filename = 'color_meter_failed_yuv_cap_json.json'
    ref_rgb_filename = 'color_meter_failed_rgb_ref_json.json'
    cap_rgb_filename = 'color_meter_failed_rgb_cap_json.json'
    ref_hsv_filename = 'color_meter_failed_hsv_ref_json.json'
    cap_hsv_filename = 'color_meter_failed_hsv_cap_json.json'

    with self.assertRaises(AttributeError):
      ref_ser = ip.colorjson.JsonSerializerYUV(ref_yuv_filename)
      cap_ser = ip.colorjson.JsonSerializerYUV(cap_yuv_filename)
      ref_ser.write()
      cap_ser.write()
      ref_dser = ip.colorjson.JsonDeserializer(ref_yuv_filename)
      cap_dser = ip.colorjson.JsonDeserializer(cap_yuv_filename)
      color_meter = ip.colormeter.ColorMeter(ref_dser, cap_dser)
      avg = color_meter.get_hls_delta_perc()

    with self.assertRaises(AttributeError):
      ref_ser = ip.colorjson.JsonSerializerRGB(ref_rgb_filename)
      cap_ser = ip.colorjson.JsonSerializerRGB(cap_rgb_filename)
      ref_ser.write()
      cap_ser.write()
      ref_dser = ip.colorjson.JsonDeserializer(ref_rgb_filename)
      cap_dser = ip.colorjson.JsonDeserializer(cap_rgb_filename)
      color_meter = ip.colormeter.ColorMeter(ref_dser, cap_dser)
      avg = color_meter.get_hls_delta_perc()

    with self.assertRaises(AttributeError):
      ref_ser = ip.colorjson.JsonSerializerRGB(ref_hsv_filename)
      cap_ser = ip.colorjson.JsonSerializerRGB(cap_hsv_filename)
      ref_ser.write()
      cap_ser.write()
      ref_dser = ip.colorjson.JsonDeserializer(ref_hsv_filename)
      cap_dser = ip.colorjson.JsonDeserializer(cap_hsv_filename)
      color_meter = ip.colormeter.ColorMeter(ref_dser, cap_dser)
      avg = color_meter.get_hls_delta_perc()

    os.remove(ref_rgb_filename)
    os.remove(cap_rgb_filename)
    os.remove(ref_yuv_filename)
    os.remove(cap_yuv_filename)
    os.remove(ref_hsv_filename)
    os.remove(cap_hsv_filename)

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
    try:
      fake_display = self.make_fake_display((1280, 720))
      fake_display.start()
      closer = threading.Thread(target=self.close_window)
      closer.start()
      image_loader = ip.imgloader.ImageLoaderDefault(self.res.red)
      csRGB = ip.colorreader.ColorReaderRGB(image_loader, 'test.json')
      csRGB.processing()
      closer.join()
      fake_display.stop()
    except IOError:
      pass

  def stop_gui(self, timeout, fake_display):
    sleep(timeout)
    plt.ioff()
    plt.close("all")

  def test_gui_plot(self):
    try:
      if 'TRAVIS_TEST_ONLY' in os.environ:
        fake_display = self.make_fake_display((1280, 720))
        fake_display.start()
        ref_filename = 'graph_tests_ref_json.json'
        ref_cj = ip.colorjson.JsonSerializerHLS(ref_filename)
        ref_cj.append([10, 10, 10])
        ref_cj.append([10, 10, 10])
        ref_cj.append([10, 10, 10])
        ref_cj.write()
  
        cap_filename = 'graph_tests_cap_json.json'
        cap_cj = ip.colorjson.JsonSerializerHLS(cap_filename)
        cap_cj.append([20, 20, 20])
        cap_cj.append([20, 20, 20])
        cap_cj.append([20, 20, 20])
        cap_cj.write()
  
        timeout = 3
        closer = threading.Thread(target=self.stop_gui, args=[timeout, fake_display])
        closer.start()
        graph_hs = ip.graph.GraphHS(ref_filename, cap_filename)
        graph_hs.show()
        closer.join()
        fake_display.stop()
    except IOError:
      pass

  def test_main_function(self):
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
