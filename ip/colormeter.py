#!/usr/bin/env python3
"""Calculate color paramters"""

import numpy as np
import scipy.stats as stats
import pylab as plt
import cv2

import ip.imgloader


def dist(data):
  return stats.norm.pdf(data, np.mean(data), np.std(data))

def plot_dist(data):
  plt.plot(data, dist(data), '-o')
  plt.hist(data, normed=True)
  plt.show()

class DistributionHSL:
  def __init__(self, img):
    self.__h = img[0]
    self.__s = img[1]
    self.__v = img[2]

  def show_s_plot(self):
    plot_dist(self.__s)



class ColorMeter:
  def __init__(self, ref_color, cap_color):
    self.__ref_color = ref_color
    self.__cap_color = cap_color

  def get_hls_delta_perc(self):
    if self.__ref_color.get()['format'] != 'hls' or self.__cap_color.get()['format'] != 'hls':
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
