#!/usr/bin/env python3.5
"""Script to read the color data of each pixel"""

import abc
import argparse
import sys
import os
import cv2

class ColorReader(metaclass=abc.ABCMeta):
  def __init__(self, filename):
    self.__filename = filename
    self.__window = self.__filename
    self._img = cv2.imread(self.__filename)

  @abc.abstractmethod
  def _read_colors(self, pos):
    pass

  def __mouse_event_processing(self, pos):
    self._read_colors(pos)

  def __on_mouse_event(self, event, pos_x, pos_y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
      self.__mouse_event_processing((pos_x, pos_y))

  def processing(self):
    cv2.imshow(self.__filename, self._img)
    cv2.setMouseCallback(self.__window, self.__on_mouse_event)
    while True:
      pressedkey = cv2.waitKey(100)
      if pressedkey == 27:
        cv2.destroyAllWindows()
        break
      if cv2.getWindowProperty(self.__window, cv2.WND_PROP_VISIBLE) < 1:
        break
    cv2.destroyAllWindows()


class ColorReaderRGB(ColorReader):
  def __init__(self, filename):
    super().__init__(filename)
    print('R\tG\tB')

  def _read_colors(self, pos):
    super()._read_colors(pos)
    pos_x, pos_y = pos
    color_rgb = self._img[pos_y, pos_x, :]
    val_b, val_g, val_r = color_rgb
    print(val_r, '\t', val_g, '\t', val_b)


class ColorReaderYUV(ColorReader):
  def __init__(self, filename):
    super().__init__(filename)
    print('Y\tU\tV')

  def _read_colors(self, pos):
    super()._read_colors(pos)
    pos_x, pos_y = pos
    img_yuv = cv2.cvtColor(self._img, cv2.COLOR_BGR2YUV)
    color_yuv = img_yuv[pos_y, pos_x, :]
    val_y, val_u, val_v = color_yuv
    print(val_y, '\t', val_u, '\t', val_v)

def make_color_reader(color_format, img_file):
  if color_format == 'rgb':
    return ColorReaderRGB(img_file)
  if color_format == 'yuv':
    return ColorReaderYUV(img_file)
  raise AttributeError('Color format: ' + color_format + ' not found')

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-i', '--imgfile', type=str, help='Image file', default='')
  parser.add_argument('-f', '--format', type=str, help='RGB, YUV (Default: RGB)', default='RGB')

  args = parser.parse_args()
  img_format = args.format.lower()
  img_file = args.imgfile

  if not os.path.exists(img_file):
    print('File not found')
    sys.exit(1)

  try:
    color_reader = make_color_reader(img_format, img_file)
    color_reader.processing()
  except AttributeError:
    err = sys.exc_info()[1]
    print('Cannot read color: ', err)

if __name__ == '__main__':
  main()
