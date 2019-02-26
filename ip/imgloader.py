#!/usr/bin/env python3
"""Image file loader"""

import abc
import numpy as np
import cv2


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
    if pixel_format == 'i420':
      return ImageLoaderRawI420(img_filename, size)
    if pixel_format == '':
      return ImageLoaderDefault(img_filename)
    raise AttributeError('image_loader_factory: ' + pixel_format + ' not found')

  def get_native_channels(self):
    pass


class ImageLoaderDefault(ImageLoader):
  def __init__(self, filename):
    self.__filename = filename

  def imread(self):
    return cv2.imread(self.__filename)

  def get_native_channels(self):
    return self.imread()


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

  def get_native_channels(self):
    bgr_converted_yuv = self.imread()
    return  cv2.cvtColor(bgr_converted_yuv, cv2.COLOR_BGR2YUV)


class ImageLoaderRawNV12(ImageLoaderRawNV21):
  def imread(self):
    raw_img = self._read_raw()
    return cv2.cvtColor(raw_img, cv2.COLOR_YUV2BGR_NV12)

  def get_native_channels(self):
    bgr_converted_yuv = self.imread()
    return  cv2.cvtColor(bgr_converted_yuv, cv2.COLOR_BGR2YUV)

class ImageLoaderRawI420(ImageLoaderRawNV21):
  def imread(self):
    raw_img = self._read_raw()
    return cv2.cvtColor(raw_img, cv2.COLOR_YUV2BGR_I420)


def create(img_filename, pixel_format='', size=None):
  return ImageLoader.create(img_filename, pixel_format, size)
