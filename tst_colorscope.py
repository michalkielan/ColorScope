import unittest
import colorscope
from xvfbwrapper import Xvfb

class Resources:
  img_00_path = 'res/test_img/pallete_00.jpg'


res = Resources()

class TestColorScope(unittest.TestCase):
  def setUp(self):
    self.xvfb = Xvfb(width = 1280, height = 720)
    self.addCleanup(self.xvfb.stop)
    self.xvfb.start()

  def testFactoryCreate(self):
    colorscope.make_color_reader('rgb', res.img_00_path)
    colorscope.make_color_reader('yuv', res.img_00_path)

    with self.assertRaises(AttributeError):
      colorscope.make_color_reader('', '')

    with self.assertRaises(AttributeError):
      colorscope.make_color_reader('invalid', '')

  def testColorScopeInstances(self):
    csRGB = colorscope.ColorReaderRGB(res.img_00_path)
    csYUV = colorscope.ColorReaderYUV(res.img_00_path)

    with self.assertRaises(TypeError):
      csINV = colorscope.ColorReader(res.img_00_path)


if __name__ == '__main__':
  unittest.main()
