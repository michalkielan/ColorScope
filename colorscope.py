#!/usr/bin/env python3.5
"""Script to read the color values"""

import abc
import argparse
import sys
import os
import numpy as np
import cv2


class ColorChannelFilter:
  def __init__(self, img):
    self.__img = img
    self.__channel_data = self.__get_channel_data()

  def __get_channel_data(self):
    h, w, num_channels = self.__img.shape
    channel_data = [[] for i in range(num_channels)]
    for y in range(0, h):
      for x in range(0, w):
        channels = self.__img[y, x, :]
        for i in range(0, num_channels):
          channel_data[i].append(int(channels[i]))
    return channel_data

  def median(self):
    channel_filtered = []
    for channel_val in self.__channel_data:
      channel_filtered.append(int(np.median(channel_val)))
    return channel_filtered

  def average(self):
    channel_filtered = []
    for channel_val in self.__channel_data:
      channel_filtered.append(int(np.average(channel_val)))
    return channel_filtered


class RectDrawer:
  def __init__(self, window, image, color):
    self.__is_draw = False
    self.__start_pos = [0, 0]
    self.__color = color
    self.__window = window
    self.__img = image
    self.__img_mark = self.__img.copy()

  def start(self, pos):
    self.__is_draw = True
    self.__start_pos = pos

  def draw(self, pos):
    if self.__is_draw:
      self.__img = self.__img_mark.copy()
      cv2.rectangle(self.__img, self.__start_pos, pos, self.__color, 1)
      cv2.imshow(self.__window, self.__img)

  def end(self, pos):
    self.__is_draw = False
    cv2.rectangle(self.__img, self.__start_pos, pos, self.__color, 1)
    cv2.imshow(self.__window, self.__img)


class ImageLoader(metaclass=abc.ABCMeta):
  @abc.abstractmethod
  def imread(self):
    pass

  @staticmethod
  def create(img_filename, pixel_format='', size=None):
    if pixel_format == 'nv21':
      return ImageLoaderRawNV21(img_filename, size)
    if pixel_format == 'nv12':
      return ImageLoaderRawNV12(img_filename, size)
    if pixel_format == '':
      return ImageLoaderDefault(img_filename)
    raise AttributeError('image_loader_factory: ' + pixel_format + ' not found')


class ImageLoaderDefault(ImageLoader):
  def __init__(self, filename):
    self.__filename = filename

  def imread(self):
    return cv2.imread(self.__filename)


class ImageLoaderRawNV21(ImageLoader):
  def __init__(self, filename, size):
    width, height = size
    self.__frame_len = width * height * 3 / 2
    self.__img_file = open(filename, 'rb')
    self.__shape = (int(height * 1.5), width)

  def _read_raw(self):
    raw = self.__img_file.read(int(self.__frame_len))
    buf = np.frombuffer(raw, dtype=np.uint8)
    raw_img = buf.reshape(self.__shape)
    return raw_img

  def imread(self):
    raw_img = self._read_raw()
    return cv2.cvtColor(raw_img, cv2.COLOR_YUV2BGR_NV21)


class ImageLoaderRawNV12(ImageLoaderRawNV21):
  def imread(self):
    raw_img = self._read_raw()
    return cv2.cvtColor(raw_img, cv2.COLOR_YUV2BGR_NV12)


class ColorReader(metaclass=abc.ABCMeta):
  def __init__(self, image_loader):
    rect_color = (0, 0, 255)
    self.__window = 'ColorScope'
    self._img = image_loader.imread()
    if self._img is None:
      raise AttributeError('ColorReader.__init__: image load failed')

    self._img_mark = self._img.copy()
    self.__drawer = RectDrawer(self.__window, self._img, rect_color)
    self.__rect = [[0, 0], [0, 0]]

  @abc.abstractmethod
  def _get_color_format(self, img_roi):
    pass

  def read_rect_color(self, rect):
    p1_x, p1_y = [rect[0][0], rect[0][1]]
    p2_x, p2_y = [rect[1][0], rect[1][1]]

    min_x, min_y = [min(p1_x, p2_x), min(p1_y, p2_y)]
    max_x, max_y = [max(p1_x, p2_x), max(p1_y, p2_y)]

    roi = self._img[min_y:max_y, min_x:max_x]

    color_filter = ColorChannelFilter(self._get_color_format(roi))
    return color_filter.median()

  def __on_mouse_event(self, event, x, y, flags, param):
    del flags, param
    if event == cv2.EVENT_LBUTTONDOWN:
      self.__drawer.start((x, y))
      self.__rect[0] = [x, y]

    elif event == cv2.EVENT_MOUSEMOVE:
      self.__drawer.draw((x, y))

    elif event == cv2.EVENT_LBUTTONUP:
      self.__drawer.end((x, y))
      self.__rect[1] = [x, y]
      if self.__rect[0] != self.__rect[1]:
        color = self.read_rect_color(self.__rect)
        print(color[0], color[1], color[2], sep='\t')

  def processing(self):
    cv2.imshow(self.__window, self._img)
    cv2.setMouseCallback(self.__window, self.__on_mouse_event)
    while True:
      pressedkey = cv2.waitKey(100)
      if pressedkey == 27 or pressedkey == ord('q'):
        cv2.destroyAllWindows()
        break
      if cv2.getWindowProperty(self.__window, cv2.WND_PROP_VISIBLE) < 1:
        break
    cv2.destroyAllWindows()

  @staticmethod
  def create(color_format, image_loader):
    if color_format == 'rgb':
      return ColorReaderRGB(image_loader)
    if color_format == 'yuv':
      return ColorReaderYUV(image_loader)
    raise AttributeError('make_color_reader: ' + color_format + ' not found')


class ColorReaderRGB(ColorReader):
  def __init__(self, filename):
    super().__init__(filename)
    print('R', 'G', 'B', sep='\t')

  def _get_color_format(self, img_roi):
    return cv2.cvtColor(img_roi, cv2.COLOR_BGR2RGB)


class ColorReaderYUV(ColorReader):
  def __init__(self, filename):
    super().__init__(filename)
    print('Y', 'U', 'V', sep='\t')

  def _get_color_format(self, img_roi):
    return cv2.cvtColor(img_roi, cv2.COLOR_BGR2YUV)


def parse_video_size_arg(video_size):
  if video_size != '':
    w, h = video_size.split('x', 1)
    return int(w), int(h)
  return None

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '-i',
      '--imgfile',
      type=str,
      help='Image file',
      default=''
  )

  parser.add_argument(
      '-pix_fmt',
      '--pixel_format',
      type=str, help='Raw input pixel format: nv21, nv12',
      default=''
  )

  parser.add_argument(
      '-s',
      '--video_size',
      type=str, help='WxH set the frame size',
      default=''
  )

  parser.add_argument(
      '-out_fmt',
      '--output_format',
      type=str,
      help='Output rgb, yuv (Default: rgb)',
      default='rgb'
  )

  args = parser.parse_args()
  pixel_format = args.pixel_format.lower()
  output_format = args.output_format.lower()
  video_size = parse_video_size_arg(args.video_size)
  img_file = args.imgfile

  if not os.path.exists(img_file):
    sys.exit('File not found')

  image_loader = ImageLoader.create(img_file, pixel_format, video_size)

  try:
    color_reader = ColorReader.create(output_format, image_loader)
    color_reader.processing()
  except (AttributeError, ValueError) as err:
    err = sys.exc_info()[1]
    sys.exit('Cannot read image: ' + str(err))


if __name__ == '__main__':
  main()
