import unittest
import threading
import os
import sys
from time import sleep
import matplotlib.pyplot as plt
from PIL import Image
from numpy import inf
import cv2
import ip

# pylint: disable=unused-import
# pylint: disable=too-many-locals
import colorscope

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

def is_travis():
  if 'TRAVIS_TEST_ONLY' in os.environ:
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


def make_fake_display(size):
  if fake_xwindow_supported():
    w, h = size
    fake_display = Xvfb(width=w, height=h)
    return fake_display
  raise IOError('Fake xwindow not supported')


class Resources:
  # pylint: disable=too-many-instance-attributes
  def __init__(self):
    size = (10, 10)
    self.rect = [[1, 1], [5, 5]]

    if not is_windows():
      os.system(
          'ffmpeg -y \
          -nostats -loglevel 0 \
          -f rawvideo \
          -video_size 1280x720 \
          -pixel_format nv12 \
          -i /dev/urandom \
          -vframes 1 \
          raw_nv12_1280_720.yuv'
      )
      os.system(
          'ffmpeg -y \
          -nostats -loglevel 0 \
          -f rawvideo \
          -video_size 1280x720 \
          -pixel_format nv21 \
          -i /dev/urandom \
          -vframes 1 \
          raw_nv21_1280_720.yuv'
      )
      os.system(
          'ffmpeg -y \
          -nostats -loglevel 0 \
          -f rawvideo \
          -video_size 1920x1080 \
          -pixel_format nv12 \
          -i /dev/urandom \
          -vframes 1 \
          raw_nv12_1920_1080.yuv'
      )
      os.system(
          'ffmpeg -y \
          -nostats -loglevel 0 \
          -f rawvideo \
          -video_size 1920x1080 \
          -pixel_format nv21 \
          -i /dev/urandom \
          -vframes 1 \
          raw_nv21_1920_1080.yuv'
      )

      os.system(
          'ffmpeg -y \
          -nostats -loglevel 0 \
          -f rawvideo \
          -video_size 1920x1080 \
          -pixel_format yuv420p \
          -i /dev/urandom \
          -vframes 1 \
          raw_i420_1920_1080.yuv'
      )

      self.raw_nv12_1920_1080 = 'raw_nv12_1920_1080.yuv'
      self.raw_nv21_1920_1080 = 'raw_nv21_1920_1080.yuv'

      self.raw_nv12_1280_720 = 'raw_nv12_1280_720.yuv'
      self.raw_nv21_1280_720 = 'raw_nv21_1280_720.yuv'

      self.raw_i420_1920_1080 = 'raw_i420_1920_1080.yuv'

    self.red = 'red.png'
    self.green = 'green.png'
    self.blue = 'blue.png'
    self.black = 'black.png'
    self.white = 'white.png'

    img_red = Image.new('RGB', size, (255, 0, 0))
    img_green = Image.new('RGB', size, (0, 255, 0))
    img_blue = Image.new('RGB', size, (0, 0, 255))
    img_black = Image.new('RGB', size, (0, 0, 0))
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
  # pylint: disable=useless-super-delegation
  def read_rect_color(self, rect):
    return super().read_rect_color(rect)


class ColorReaderYuvMock(ip.colorreader.ColorReaderYUV):
  # pylint: disable=useless-super-delegation
  def read_rect_color(self, rect):
    return super().read_rect_color(rect)


class ColorReaderHsvMock(ip.colorreader.ColorReaderHSV):
  # pylint: disable=useless-super-delegation
  def read_rect_color(self, rect):
    return super().read_rect_color(rect)


class ColorReaderHlsMock(ip.colorreader.ColorReaderHLS):
  # pylint: disable=useless-super-delegation
  def read_rect_color(self, rect):
    return super().read_rect_color(rect)


class TestImgLoader(unittest.TestCase):
  def setUp(self):
    self.res = Resources()

  def test_factory_failed(self):
    with self.assertRaises(AttributeError):
      img_loader = ip.imgloader.ImageLoader.create(
          self.res.red,
          'invalid',
          (0, 0)
      )
      del img_loader


  def test_factory_nv12(self):
    if not is_windows():
      imloader = ip.imgloader.ImageLoader.create(
          self.res.raw_nv12_1920_1080,
          'nv12',
          (1920, 1080)
      )
      img = imloader.imread()
      h, w, channels = img.shape
      self.assertEqual([1080, 1920], [h, w])
      self.assertEqual(3, channels)

  def test_factory_nv21(self):
    if not is_windows():
      imloader = ip.imgloader.ImageLoader.create(
          self.res.raw_nv21_1920_1080,
          'nv21',
          (1920, 1080)
      )
      img = imloader.imread()
      h, w, channels = img.shape
      self.assertEqual([1080, 1920], [h, w])
      self.assertEqual(3, channels)

  def test_factory_i420(self):
    if not is_windows():
      imloader = ip.imgloader.ImageLoader.create(
          self.res.raw_i420_1920_1080,
          'i420',
          (1920, 1080)
      )
      img = imloader.imread()
      h, w, channels = img.shape
      self.assertEqual([1080, 1920], [h, w])
      self.assertEqual(3, channels)

  def test_factory_default(self):
    if not is_windows():
      imloader = ip.imgloader.create(self.res.red)
      img = imloader.imread()
      h, w, channels = img.shape
      self.assertEqual([10, 10], [h, w])
      self.assertEqual(3, channels)
      del img

  def test_factory_wrong_size(self):
    if not is_windows():
      with self.assertRaises(ValueError):
        imloader = ip.imgloader.ImageLoader.create(
            self.res.raw_nv21_1920_1080,
            'nv21',
            (2000, 2000)
        )
        ip.colorreader.ColorReader.create('rgb', imloader, '', '')

  def test_nv12_1080p(self):
    if not is_windows():
      imloader = ip.imgloader.ImageLoaderRawNV12(
          self.res.raw_nv12_1920_1080,
          (1920, 1080)
      )
      img = imloader.imread()
      h, w, channels = img.shape
      self.assertEqual([1080, 1920], [h, w])
      self.assertEqual(3, channels)

  def test_nv12_720p(self):
    if not is_windows():
      imloader = ip.imgloader.ImageLoaderRawNV12(
          self.res.raw_nv12_1280_720,
          (1280, 720)
      )
      img = imloader.imread()
      h, w, channels = img.shape
      self.assertEqual([720, 1280], [h, w])
      self.assertEqual(3, channels)

  def test_nv21_1080p(self):
    if not is_windows():
      imloader = ip.imgloader.ImageLoaderRawNV21(
          self.res.raw_nv21_1920_1080,
          (1920, 1080)
      )
      img = imloader.imread()
      h, w, channels = img.shape
      self.assertEqual([1080, 1920], [h, w])
      self.assertEqual(3, channels)

  def test_nv21_720p(self):
    if not is_windows():
      imloader = ip.imgloader.ImageLoaderRawNV21(
          self.res.raw_nv21_1280_720,
          (1280, 720)
      )
      img = imloader.imread()
      h, w, channels = img.shape
      self.assertEqual([720, 1280], [h, w])
      self.assertEqual(3, channels)


# pylint: disable=too-many-public-methods
class TestColorReader(unittest.TestCase):
  def setUp(self):
    self.res = Resources()

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
    cr_rgb = ip.colorreader.ColorReaderRGB(imloader, 'test.json')
    cr_yuv = ip.colorreader.ColorReaderYUV(imloader, 'test.json')
    cr_hsv = ip.colorreader.ColorReaderHSV(imloader, 'test.json')
    cr_hls = ip.colorreader.ColorReaderHLS(imloader, 'test.json')
    del cr_rgb
    del cr_yuv
    del cr_hsv
    del cr_hls

    with self.assertRaises(TypeError):
      # pylint: disable=abstract-class-instantiated
      # pylint: disable=no-value-for-parameter
      cr_inv = ip.colorreader.ColorReader(imloader)
      del cr_inv

  def test_color_rgb_red(self):
    img_file = self.res.red
    img_loader = ip.imgloader.ImageLoaderDefault(img_file)
    crm = ColorReaderRgbMock(img_loader, 'test.json')
    rgb = crm.read_rect_color(self.res.rect)
    self.assertEqual(rgb, [255, 0, 0])

  def test_color_hsv_red(self):
    img_file = self.res.red
    img_loader = ip.imgloader.ImageLoaderDefault(img_file)
    crm = ColorReaderHsvMock(img_loader, 'test.json')
    hsv = crm.read_rect_color(self.res.rect)
    self.assertEqual(hsv, [0, 255, 255])

  def test_color_hls_red(self):
    img_file = self.res.red
    img_loader = ip.imgloader.ImageLoaderDefault(img_file)
    crm = ColorReaderHlsMock(img_loader, 'test.json')
    hls = crm.read_rect_color(self.res.rect)
    self.assertEqual(hls, [0, 128, 255])

  def test_color_yuv_red(self):
    img_file = self.res.red
    img_loader = ip.imgloader.ImageLoaderDefault(img_file)
    crm = ColorReaderYuvMock(img_loader, 'test.json')
    yuv = crm.read_rect_color(self.res.rect)
    self.assertEqual(yuv, [76, 91, 255])

  def test_color_rgb_green(self):
    img_file = self.res.green
    img_loader = ip.imgloader.ImageLoaderDefault(img_file)
    crm = ColorReaderRgbMock(img_loader, 'test.json')
    rgb = crm.read_rect_color(self.res.rect)
    self.assertEqual(rgb, [0, 255, 0])

  def test_color_hsv_green(self):
    img_file = self.res.green
    img_loader = ip.imgloader.ImageLoaderDefault(img_file)
    crm = ColorReaderHsvMock(img_loader, 'test.json')
    hsv = crm.read_rect_color(self.res.rect)
    self.assertEqual(hsv, [60, 255, 255])

  def test_color_hls_green(self):
    img_file = self.res.green
    img_loader = ip.imgloader.ImageLoaderDefault(img_file)
    crm = ColorReaderHlsMock(img_loader, 'test.json')
    hls = crm.read_rect_color(self.res.rect)
    self.assertEqual(hls, [60, 128, 255])

  def test_color_yuv_green(self):
    img_file = self.res.green
    img_loader = ip.imgloader.ImageLoaderDefault(img_file)
    crm = ColorReaderYuvMock(img_loader, 'test.json')
    yuv = crm.read_rect_color(self.res.rect)
    self.assertEqual(yuv, [150, 54, 0])

  def test_color_rgb_blue(self):
    img_file = self.res.blue
    img_loader = ip.imgloader.ImageLoaderDefault(img_file)
    crm = ColorReaderRgbMock(img_loader, 'test.json')
    rgb = crm.read_rect_color(self.res.rect)
    self.assertEqual(rgb, [0, 0, 255])

  def test_color_hsv_blue(self):
    img_file = self.res.blue
    img_loader = ip.imgloader.ImageLoaderDefault(img_file)
    crm = ColorReaderHsvMock(img_loader, 'test.json')
    hsv = crm.read_rect_color(self.res.rect)
    self.assertEqual(hsv, [120, 255, 255])

  def test_color_hls_blue(self):
    img_file = self.res.blue
    img_loader = ip.imgloader.ImageLoaderDefault(img_file)
    crm = ColorReaderHlsMock(img_loader, 'test.json')
    hls = crm.read_rect_color(self.res.rect)
    self.assertEqual(hls, [120, 128, 255])

  def test_color_yuv_blue(self):
    img_file = self.res.blue
    img_loader = ip.imgloader.ImageLoaderDefault(img_file)
    crm = ColorReaderYuvMock(img_loader, 'test.json')
    yuv = crm.read_rect_color(self.res.rect)
    self.assertEqual(yuv, [29, 239, 103])

  def test_color_rgb_black(self):
    img_file = self.res.black
    img_loader = ip.imgloader.ImageLoaderDefault(img_file)
    crm = ColorReaderRgbMock(img_loader, 'test.json')
    rgb = crm.read_rect_color(self.res.rect)
    self.assertEqual(rgb, [0, 0, 0])

  def test_color_hsv_black(self):
    img_file = self.res.black
    img_loader = ip.imgloader.ImageLoaderDefault(img_file)
    crm = ColorReaderHsvMock(img_loader, 'test.json')
    hsv = crm.read_rect_color(self.res.rect)
    self.assertEqual(hsv, [0, 0, 0])

  def test_color_hls_black(self):
    img_file = self.res.black
    img_loader = ip.imgloader.ImageLoaderDefault(img_file)
    crm = ColorReaderHlsMock(img_loader, 'test.json')
    hls = crm.read_rect_color(self.res.rect)
    self.assertEqual(hls, [0, 0, 0])

  def test_color_yuv_black(self):
    img_file = self.res.black
    img_loader = ip.imgloader.ImageLoaderDefault(img_file)
    crm = ColorReaderYuvMock(img_loader, 'test.json')
    yuv = crm.read_rect_color(self.res.rect)
    self.assertEqual(yuv, [0, 128, 128])

  def test_color_rgb_white(self):
    img_file = self.res.white
    img_loader = ip.imgloader.ImageLoaderDefault(img_file)
    crm = ColorReaderRgbMock(img_loader, 'test.json')
    rgb = crm.read_rect_color(self.res.rect)
    self.assertEqual(rgb, [255, 255, 255])

  def test_color_hsv_white(self):
    img_file = self.res.white
    img_loader = ip.imgloader.ImageLoaderDefault(img_file)
    crm = ColorReaderHsvMock(img_loader, 'test.json')
    hsv = crm.read_rect_color(self.res.rect)
    self.assertEqual(hsv, [0, 0, 255])

  def test_color_hls_white(self):
    img_file = self.res.white
    img_loader = ip.imgloader.ImageLoaderDefault(img_file)
    crm = ColorReaderHlsMock(img_loader, 'test.json')
    hls = crm.read_rect_color(self.res.rect)
    self.assertEqual(hls, [0, 255, 0])

  def test_color_yuv_white(self):
    img_file = self.res.white
    img_loader = ip.imgloader.ImageLoaderDefault(img_file)
    crm = ColorReaderYuvMock(img_loader, 'test.json')
    yuv = crm.read_rect_color(self.res.rect)
    self.assertEqual(yuv, [255, 128, 128])



class TestColorFilter(unittest.TestCase):
  def setUp(self):
    self.res = Resources()

  def test_color_filter_median_red(self):
    img_file = self.res.red
    color_filter = ip.colorfilter.ColorChannelFilterMedian()
    # pylint: disable=unbalanced-tuple-unpacking
    r, g, b = color_filter.filter(cv2.imread(img_file))
    self.assertEqual([b, g, r], [255, 0, 0])

  def test_color_filter_average_red(self):
    img_file = self.res.red
    color_filter = ip.colorfilter.ColorChannelFilterAverage()
    # pylint: disable=unbalanced-tuple-unpacking
    r, g, b = color_filter.filter(cv2.imread(img_file))
    self.assertEqual([b, g, r], [255, 0, 0])

  def test_color_filter_median_green(self):
    img_file = self.res.green
    color_filter = ip.colorfilter.ColorChannelFilterMedian()
    # pylint: disable=unbalanced-tuple-unpacking
    r, g, b = color_filter.filter(cv2.imread(img_file))
    self.assertEqual([b, g, r], [0, 255, 0])

  def test_color_filter_average_green(self):
    img_file = self.res.green
    color_filter = ip.colorfilter.ColorChannelFilterAverage()
    # pylint: disable=unbalanced-tuple-unpacking
    r, g, b = color_filter.filter(cv2.imread(img_file))
    self.assertEqual([b, g, r], [0, 255, 0])

  def test_color_filter_median_blue(self):
    img_file = self.res.blue
    color_filter = ip.colorfilter.ColorChannelFilterMedian()
    # pylint: disable=unbalanced-tuple-unpacking
    r, g, b = color_filter.filter(cv2.imread(img_file))
    self.assertEqual([b, g, r], [0, 0, 255])

  def test_color_filter_average_blue(self):
    img_file = self.res.blue
    color_filter = ip.colorfilter.ColorChannelFilterAverage()
    # pylint: disable=unbalanced-tuple-unpacking
    r, g, b = color_filter.filter(cv2.imread(img_file))
    self.assertEqual([b, g, r], [0, 0, 255])

  def test_color_filter_median_black(self):
    img_file = self.res.black
    color_filter = ip.colorfilter.ColorChannelFilterMedian()
    # pylint: disable=unbalanced-tuple-unpacking
    r, g, b = color_filter.filter(cv2.imread(img_file))
    self.assertEqual([b, g, r], [0, 0, 0])

  def test_color_filter_average_black(self):
    img_file = self.res.black
    color_filter = ip.colorfilter.ColorChannelFilterAverage()
    # pylint: disable=unbalanced-tuple-unpacking
    r, g, b = color_filter.filter(cv2.imread(img_file))
    self.assertEqual([b, g, r], [0, 0, 0])

  def test_color_filter_median_white(self):
    img_file = self.res.white
    color_filter = ip.colorfilter.ColorChannelFilterMedian()
    # pylint: disable=unbalanced-tuple-unpacking
    r, g, b = color_filter.filter(cv2.imread(img_file))
    self.assertEqual([b, g, r], [255, 255, 255])

  def test_color_filter_average_white(self):
    img_file = self.res.white
    color_filter = ip.colorfilter.ColorChannelFilterAverage()
    # pylint: disable=unbalanced-tuple-unpacking
    r, g, b = color_filter.filter(cv2.imread(img_file))
    self.assertEqual([b, g, r], [255, 255, 255])


class TestGraph(unittest.TestCase):
  def setUp(self):
    self.res = Resources()

  def test_const(self):
    self.assertEqual(ip.graph.Const.get_max_hue(), 179)
    self.assertEqual(ip.graph.Const.get_max_saturation(), 255)
    self.assertEqual(ip.graph.Const.get_max_lightness(), 255)
    self.assertEqual(ip.graph.Const.Symbols.delta(), '\u0394')


class TestColorJson(unittest.TestCase):
  def setUp(self):
    self.res = Resources()

  def test_json_rgb(self):
    json_filename = 'rgb_json.json'
    jss = ip.colorjson.JsonSerializerRGB(json_filename)
    jss.append([254, 219, 21])
    jss.append([237, 254, 51])
    jss.append([254, 250, 168])
    jss.write()

    jsd = ip.colorjson.JsonDeserializer(json_filename)
    self.assertEqual('rgb', jsd.get()['format'])
    self.assertEqual([254, 237, 254], jsd.get()['channels']['r'])
    self.assertEqual([219, 254, 250], jsd.get()['channels']['g'])
    self.assertEqual([21, 51, 168], jsd.get()['channels']['b'])
    os.remove(json_filename)

  def test_json_yuv(self):
    json_filename = 'yuv_json.json'
    jss = ip.colorjson.JsonSerializerYUV(json_filename)
    jss.append([0, 128, 128])
    jss.append([185, 82, 188])
    jss.append([248, 114, 133])
    jss.write()

    jsd = ip.colorjson.JsonDeserializer(json_filename)
    self.assertEqual('yuv', jsd.get()['format'])
    self.assertEqual([0, 185, 248], jsd.get()['channels']['y'])
    self.assertEqual([128, 82, 114], jsd.get()['channels']['u'])
    self.assertEqual([128, 188, 133], jsd.get()['channels']['v'])
    os.remove(json_filename)

  def test_json_hsv(self):
    json_filename = 'hsv_json.json'
    jss = ip.colorjson.JsonSerializerHSV(json_filename)
    jss.append([24, 227, 255])
    jss.append([1, 217, 254])
    jss.append([112, 145, 254])
    jss.write()

    jsd = ip.colorjson.JsonDeserializer(json_filename)
    self.assertEqual('hsv', jsd.get()['format'])
    self.assertEqual([24, 1, 112], jsd.get()['channels']['h'])
    self.assertEqual([227, 217, 145], jsd.get()['channels']['s'])
    self.assertEqual([255, 254, 254], jsd.get()['channels']['v'])
    os.remove(json_filename)

  def test_json_hls(self):
    json_filename = 'hls_json.json'
    jss = ip.colorjson.JsonSerializerHLS(json_filename)
    jss.append([9, 155, 237])
    jss.append([61, 234, 253])
    jss.append([150, 166, 254])
    jss.write()

    jsd = ip.colorjson.JsonDeserializer(json_filename)
    self.assertEqual('hls', jsd.get()['format'])
    self.assertEqual([9, 61, 150], jsd.get()['channels']['h'])
    self.assertEqual([155, 234, 166], jsd.get()['channels']['l'])
    self.assertEqual([237, 253, 254], jsd.get()['channels']['s'])
    os.remove(json_filename)


class TestColorMeter(unittest.TestCase):
  def setUp(self):
    self.res = Resources()

  def test_colormeter(self):
    ref_filename = 'color_meter_tests_ref_json.json'
    ref_jss = ip.colorjson.JsonSerializerHLS(ref_filename)
    ref_jss.append([10, 10, 10])
    ref_jss.append([10, 10, 10])
    ref_jss.append([10, 10, 10])
    ref_jss.write()

    cap_filename = 'color_meter_tests_cap_json.json'
    cap_jss = ip.colorjson.JsonSerializerHLS(cap_filename)
    cap_jss.append([20, 20, 20])
    cap_jss.append([20, 20, 20])
    cap_jss.append([20, 20, 20])
    cap_jss.write()

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
      del avg

    with self.assertRaises(AttributeError):
      ref_ser = ip.colorjson.JsonSerializerRGB(ref_rgb_filename)
      cap_ser = ip.colorjson.JsonSerializerRGB(cap_rgb_filename)
      ref_ser.write()
      cap_ser.write()
      ref_dser = ip.colorjson.JsonDeserializer(ref_rgb_filename)
      cap_dser = ip.colorjson.JsonDeserializer(cap_rgb_filename)
      color_meter = ip.colormeter.ColorMeter(ref_dser, cap_dser)
      avg = color_meter.get_hls_delta_perc()
      del avg

    with self.assertRaises(AttributeError):
      ref_ser = ip.colorjson.JsonSerializerRGB(ref_hsv_filename)
      cap_ser = ip.colorjson.JsonSerializerRGB(cap_hsv_filename)
      ref_ser.write()
      cap_ser.write()
      ref_dser = ip.colorjson.JsonDeserializer(ref_hsv_filename)
      cap_dser = ip.colorjson.JsonDeserializer(cap_hsv_filename)
      color_meter = ip.colormeter.ColorMeter(ref_dser, cap_dser)
      avg = color_meter.get_hls_delta_perc()
      del avg

    os.remove(ref_rgb_filename)
    os.remove(cap_rgb_filename)
    os.remove(ref_yuv_filename)
    os.remove(cap_yuv_filename)
    os.remove(ref_hsv_filename)
    os.remove(cap_hsv_filename)


class TestGui(unittest.TestCase):
  def setUp(self):
    self.res = Resources()
    self.fake_gui_enabled = False
    try:
      self.fake_display = make_fake_display((1280, 720))
      self.fake_display.start()
      self.fake_gui_enabled = True
      self.addCleanup(self.fake_display.stop)
    except IOError:
      pass

  def close_window(self):
    if self.fake_gui_enabled:
      fake_mouse = FakeMouse()
      fake_keyboard = FakeKeyboard()
      start_pos = [50, 50]
      timeout = 3
      x, y = start_pos

      sleep(timeout)
      fake_mouse.click(x, y)
      fake_keyboard.tap_esc()
  def gui_open_close_tst(self):
    if self.fake_gui_enabled:
      closer = threading.Thread(target=self.close_window)
      closer.start()
      image_loader = ip.imgloader.ImageLoaderDefault(self.res.red)
      cr_rgb = ip.colorreader.ColorReaderRGB(image_loader, 'test.json')
      cr_rgb.processing()
      closer.join()

  @staticmethod
  def stop_gui(timeout):
    sleep(timeout)
    plt.ioff()
    plt.close("all")

  def gui_plot(self):
    if self.fake_gui_enabled:
      if is_travis():
        ref_filename = 'graph_tests_ref_json.json'
        ref_jss = ip.colorjson.JsonSerializerHLS(ref_filename)
        ref_jss.append([10, 10, 10])
        ref_jss.append([10, 10, 10])
        ref_jss.append([10, 10, 10])
        ref_jss.write()

        cap_filename = 'graph_tests_cap_json.json'
        cap_jss = ip.colorjson.JsonSerializerHLS(cap_filename)
        cap_jss.append([20, 20, 20])
        cap_jss.append([20, 20, 20])
        cap_jss.append([20, 20, 20])
        cap_jss.write()

        timeout = 3
        closer = threading.Thread(target=self.stop_gui, args=[timeout])
        closer.start()
        graph_hs = ip.graph.GraphHS(ref_filename, cap_filename)
        graph_hs.show()
        closer.join()

  # pylint: disable=too-many-statements
  def draw_rect(self):
    if self.fake_gui_enabled:
      color_background = (20, 20, 20)
      color_rect = [0, 0, 255]
      file_name = 'tmp_img.jpg'
      window = 'tmp_window'
      img_file = Image.new('RGB', (500, 500), color_background)
      img_file.save(file_name)
      img = cv2.imread(file_name)
      cv2.imshow(window, img)
      rect_drawer = ip.draw.RectDrawer(window, img, color_rect)
      rect_drawer.start((10, 10))
      rect_drawer.end((14, 14))

      self.assertEqual(img[10][10][0], color_rect[0])
      self.assertEqual(img[10][10][1], color_rect[1])
      self.assertEqual(img[10][10][2], color_rect[2])

      self.assertEqual(img[14][14][0], color_rect[0])
      self.assertEqual(img[14][14][1], color_rect[1])
      self.assertEqual(img[14][14][2], color_rect[2])

      self.assertEqual(img[13][13][0], color_background[0])
      self.assertEqual(img[13][13][1], color_background[1])
      self.assertEqual(img[13][13][2], color_background[2])

      rect_drawer.start((20, 20))
      rect_drawer.end((18, 18))

      self.assertEqual(img[20][20][0], color_rect[0])
      self.assertEqual(img[20][20][1], color_rect[1])
      self.assertEqual(img[20][20][2], color_rect[2])

      self.assertEqual(img[18][18][0], color_rect[0])
      self.assertEqual(img[18][18][1], color_rect[1])
      self.assertEqual(img[18][18][2], color_rect[2])

      self.assertEqual(img[17][17][0], color_background[0])
      self.assertEqual(img[17][17][1], color_background[1])
      self.assertEqual(img[17][17][2], color_background[2])

      rect_drawer.start((30, 30))
      rect_drawer.end((40, 20))

      self.assertEqual(img[30][30][0], color_rect[0])
      self.assertEqual(img[30][30][1], color_rect[1])
      self.assertEqual(img[30][30][2], color_rect[2])

      self.assertEqual(img[20][40][0], color_rect[0])
      self.assertEqual(img[20][40][1], color_rect[1])
      self.assertEqual(img[20][40][2], color_rect[2])

      self.assertEqual(img[17][17][0], color_background[0])
      self.assertEqual(img[17][17][1], color_background[1])
      self.assertEqual(img[17][17][2], color_background[2])

      rect_drawer.start((160, 160))
      rect_drawer.end((50, 70))

      self.assertEqual(img[160][160][0], color_rect[0])
      self.assertEqual(img[160][160][1], color_rect[1])
      self.assertEqual(img[160][160][2], color_rect[2])

      self.assertEqual(img[70][50][0], color_rect[0])
      self.assertEqual(img[70][50][1], color_rect[1])
      self.assertEqual(img[70][50][2], color_rect[2])
      cv2.destroyAllWindows()

  def test_gui(self):
    self.draw_rect()
    self.gui_plot()
    self.gui_open_close_tst()


class TestColorscope(unittest.TestCase):
  def setUp(self):
    self.res = Resources()

  def test_main_function(self):
    exe = ''
    if is_windows():
      exe = '%PYTHON%\\python.exe '
    else:
      exe = 'python3 '
    self.assertEqual(0, os.system(exe + ' colorscope.py -h'))
    self.assertNotEqual(0, os.system(exe + ' colorscope.py -i invalid.png'))
    self.assertNotEqual(0, os.system(exe + ' colorscope.py -i red.png -out_fmt=invalid'))
    self.assertNotEqual(0, os.system(exe + ' colorscope.py -i '))

    self.assertEqual(0, os.system(exe + ' colorscope.py --help'))
    self.assertNotEqual(0, os.system(exe + ' colorscope.py --imgfile invalid.png'))
    self.assertNotEqual(0, os.system(exe + ' colorscope.py --imgfile \
        red.png --output_format=invalid'))
    self.assertNotEqual(0, os.system(exe + ' colorscope.py --imgfile '))
    self.assertEqual(0,os.system(exe + ' colorscope.py -cp ssim  res/test_img/lena.png res/test_img/lena50.jpg'))
    self.assertEqual(0,os.system(exe + ' colorscope.py -scp ssim 0 res/test_img/lena.png res/test_img/lena50.jpg '))
    self.assertEqual(0,os.system(exe + ' colorscope.py -cp psnr res/test_img/lena.png res/test_img/lena50.jpg'))
    self.assertEqual(0,os.system(exe + ' colorscope.py -scp psnr 0 res/test_img/lena.png  res/test_img/lena50.jpg'))

class TestQualitymeasures(unittest.TestCase):
  img_res_id = 'res/test_img/'
  dir_ref_lena = os.path.join(img_res_id, 'lena.png')
  dir_cap_lena15 = os.path.join(img_res_id, 'lena15.jpg')
  dir_cap_lena50 = os.path.join(img_res_id, 'lena50.jpg')
  dir_cap_lena90 = os.path.join(img_res_id, 'lena90.jpg')

  def setUp(self):
    pass

  def test_pstnr_multichannel_rgb_same(self):
    image_loader_ref = ip.imgloader.create(self.dir_ref_lena)
    psnr1 = ip.qualitymeasurement.QualityMeasurement\
            .create(image_loader_ref, image_loader_ref, 'psnr').process()
    self.assertEqual(psnr1, inf, 'psnr =  {}'.format(psnr1))

  def test_pstnr_multichannel_rgb(self):
    image_loader_ref = ip.imgloader.create(self.dir_ref_lena)
    image_loader_cap15 = ip.imgloader.create(self.dir_cap_lena15)
    image_loader_cap50 = ip.imgloader.create(self.dir_cap_lena50)
    image_loader_cap90 = ip.imgloader.create(self.dir_cap_lena90)

    psnr15 = ip.qualitymeasurement.QualityMeasurement\
             .create(image_loader_ref, image_loader_cap15, 'psnr').process()
    psnr50 = ip.qualitymeasurement.QualityMeasurement\
             .create(image_loader_ref, image_loader_cap50, 'psnr').process()
    psnr90 = ip.qualitymeasurement.QualityMeasurement\
             .create(image_loader_ref, image_loader_cap90, 'psnr').process()

    self.assertAlmostEqual(psnr15, 28.7767, delta=0.2)
    self.assertAlmostEqual(psnr50, 31.8558, delta=0.2)
    self.assertAlmostEqual(psnr90, 36.1004, delta=0.2)


  def test_ssim_multichannel_rgb(self):
    image_loader_ref = ip.imgloader.create(self.dir_ref_lena)
    image_loader_cap15 = ip.imgloader.create(self.dir_cap_lena15)
    image_loader_cap50 = ip.imgloader.create(self.dir_cap_lena50)
    image_loader_cap90 = ip.imgloader.create(self.dir_cap_lena90)

    ssim15 = ip.qualitymeasurement.QualityMeasurement\
            .create(image_loader_ref, image_loader_cap15, 'ssim').process()
    ssim50 = ip.qualitymeasurement.QualityMeasurement\
            .create(image_loader_ref, image_loader_cap50, 'ssim').process()
    ssim90 = ip.qualitymeasurement.QualityMeasurement\
            .create(image_loader_ref, image_loader_cap90, 'ssim').process()

    self.assertAlmostEqual(ssim15, 0.764, delta=0.01)
    self.assertAlmostEqual(ssim50, 0.8353, delta=0.01)
    self.assertAlmostEqual(ssim90, 0.9045, delta=0.01)


  def test_ssim_singlechannel_rgb(self):
    image_loader_ref = ip.imgloader.create(self.dir_ref_lena)
    image_loader_cap50 = ip.imgloader.create(self.dir_cap_lena50)

    ssim50_blue = ip.qualitymeasurement.QualityMeasurement\
                  .create(image_loader_ref, image_loader_cap50, 'ssim-sc')\
                  .process(ip.qualitymeasurement.ChannelsRGB.blue)
    ssim50_green = ip.qualitymeasurement.QualityMeasurement\
                   .create(image_loader_ref, image_loader_cap50, 'ssim-sc')\
                   .process(ip.qualitymeasurement.ChannelsRGB.green)
    ssim50_red = ip.qualitymeasurement.QualityMeasurement\
                 .create(image_loader_ref, image_loader_cap50, 'ssim-sc')\
                 .process(ip.qualitymeasurement.ChannelsRGB.red)

    self.assertAlmostEqual(ssim50_blue, 0.7538, delta=0.02)
    self.assertAlmostEqual(ssim50_green, 0.8768, delta=0.02)
    self.assertAlmostEqual(ssim50_red, 0.8754, delta=0.02)

  def test_psnr_singlechannel_rgb(self):
    image_loader_ref = ip.imgloader.create(self.dir_ref_lena)
    image_loader_cap15 = ip.imgloader.create(self.dir_cap_lena15)

    psnr15_blue = ip.qualitymeasurement.QualityMeasurement\
                  .create(image_loader_ref, image_loader_cap15, 'psnr-sc')\
                  .process(ip.qualitymeasurement.ChannelsRGB.blue)
    psnr15_green = ip.qualitymeasurement.QualityMeasurement\
                   .create(image_loader_ref, image_loader_cap15, 'psnr-sc')\
                   .process(ip.qualitymeasurement.ChannelsRGB.green)
    psnr15_red = ip.qualitymeasurement.QualityMeasurement\
                 .create(image_loader_ref, image_loader_cap15, 'psnr-sc')\
                 .process(ip.qualitymeasurement.ChannelsRGB.red)

    self.assertAlmostEqual(psnr15_blue, 27.2892, delta=0.25)
    self.assertAlmostEqual(psnr15_green, 30.074, delta=0.1)
    self.assertAlmostEqual(psnr15_red, 29.4835, delta=0.25)

if __name__ == '__main__':
  unittest.main()
