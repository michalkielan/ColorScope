#!/usr/bin/env python3
"""Color data filter"""

import abc
import numpy as np


class ColorChannelFilter(metaclass=abc.ABCMeta):
  @abc.abstractmethod
  def filter(self, img):
    pass

  @staticmethod
  def _get_channel_data(img):
    h, w, num_channels = img.shape
    channel_data = [[] for i in range(num_channels)]
    for y in range(0, h):
      for x in range(0, w):
        channels = img[y, x, :]
        for i in range(0, num_channels):
          channel_data[i].append(int(channels[i]))
    return channel_data

  @staticmethod
  def create(filter_type):
    if filter_type == 'med':
      return ColorChannelFilterMedian()
    return ColorChannelFilterAverage()


class ColorChannelFilterMedian(ColorChannelFilter):
  def __median(self, img):
    channel_filtered = []
    channel_data = self._get_channel_data(img)
    for channel_val in channel_data:
      channel_filtered.append(int(np.median(channel_val)))
    return channel_filtered

  def filter(self, img):
    return self.__median(img)


class ColorChannelFilterAverage(ColorChannelFilter):
  def __average(self, img):
    channel_filtered = []
    channel_data = self._get_channel_data(img)
    for channel_val in channel_data:
      channel_filtered.append(int(np.average(channel_val)))
    return channel_filtered

  def filter(self, img):
    return self.__average(img)


def create(filter_type):
  return ColorChannelFilter.create(filter_type)
