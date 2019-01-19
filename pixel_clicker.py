#!/usr/bin/env python3.5
"""Script to read the rgb color of each pixel"""

import abc
import argparse
import sys
import os
import cv2

class ColorReader(metaclass=abc.ABCMeta):
  def __init__(self, filename):
    self.filename = filename
    self.img = cv2.imread(self.filename)

  @abc.abstractmethod
  def __read_colors__(self, pos):
    pass

  def __mouse_event_processing__(self, pos):
    self.__read_colors__(pos)

  def on_mouse_event(self, event, pos_x, pos_y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
      self.__mouse_event_processing__((pos_x, pos_y))

  def processing(self):
    cv2.imshow(self.filename, self.img)

    cv2.setMouseCallback(self.filename, self.on_mouse_event)
    pressedkey = cv2.waitKey(0)

    if pressedkey == 27:
      cv2.destroyAllWindows()


class ColorReaderRGB(ColorReader):
  def __init__(self, filename):
    super().__init__(filename)
    print('R\tG\tB')

  def __read_colors__(self, pos):
    super().__read_colors__(pos)
    pos_x, pos_y = pos
    color_rgb = self.img[pos_y, pos_x, :]
    val_b, val_g, val_r = color_rgb
    print(val_r, '\t', val_g, '\t', val_b)


class ColorReaderYUV(ColorReader):
  def __init__(self, filename):
    super().__init__(filename)
    print('Y\tU\tV')

  def __read_colors__(self, pos):
    super().__read_colors__(pos)
    pos_x, pos_y = pos
    img_yuv = cv2.cvtColor(self.img, cv2.COLOR_BGR2YUV)
    color_yuv = img_yuv[pos_y, pos_x, :]
    val_y, val_u, val_v = color_yuv
    print(val_y, '\t', val_u, '\t', val_v)


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-i', '--imgfile', type=str, help='Image file', default='')
  parser.add_argument('-f', '--format', type=str, help='RGB, YUV (Default: RGB)', default='RGB')

  args = parser.parse_args()
  img_format = args.format.lower()
  img_file = args.imgfile
  color_reader = ColorReader

  if not os.path.exists(img_file):
    print('File not found')
    sys.exit(1)

  if img_format == 'rgb':
    color_reader = ColorReaderRGB(img_file)
  elif img_format == 'yuv':
    color_reader = ColorReaderYUV(img_file)
  else:
    print('Format not found')
    sys.exit(1)

  color_reader.processing()

if __name__ == '__main__':
  main()
