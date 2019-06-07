#!/usr/bin/env python3
"""Calculate color paramters"""

import numpy as np
import matplotlib.pyplot as plt


def plot_hist(img):
  plt.hist(img.flatten(), 256, [0, 256], color='r')
  plt.xlim([0, 256])
  plt.title('Histogram')
  plt.xlabel('Color value')
  plt.ylabel('Frequency')
  plt.show()

class ColorMeter:
  def __init__(self, ref_color, cap_color):
    self.__ref_color = ref_color
    self.__cap_color = cap_color

  def get_hls_delta_perc(self):
    if (self.__ref_color.get()['format'] != 'hls' or
        self.__cap_color.get()['format'] != 'hls'):
      raise AttributeError('Color not HLS type')

    cap_channels = self.__cap_color.get()['channels']
    ref_channels = self.__ref_color.get()['channels']

    ref_h, cap_h = ref_channels['h'], cap_channels['h']
    ref_l, cap_l = ref_channels['l'], cap_channels['l']
    ref_s, cap_s = ref_channels['s'], cap_channels['s']

    delta_perc = lambda ref, cap: 0 if ref == 0 else (cap * 100.0) / ref

    delta_h_perc_data = [delta_perc(ref, cap) for ref, cap in zip(ref_h, cap_h)]
    delta_l_perc_data = [delta_perc(ref, cap) for ref, cap in zip(ref_l, cap_l)]
    delta_s_perc_data = [delta_perc(ref, cap) for ref, cap in zip(ref_s, cap_s)]

    return [
        np.average(delta_h_perc_data),
        np.average(delta_l_perc_data),
        np.average(delta_s_perc_data)
    ]
