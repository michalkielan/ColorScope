#!/usr/bin/env python3
"""Plot generator"""

import abc
import numpy as np
import cv2
import matplotlib.pyplot as plt
import ip.colorjson
import ip.colormeter


class Const:
  class Symbols:
    @staticmethod
    def delta():
      return '\u0394'

  @staticmethod
  def get_max_hue():
    return 179

  @staticmethod
  def get_max_saturation():
    return 255

  @staticmethod
  def get_max_lightness():
    return 255


def show_window(window):
  while True:
    pressed_key = cv2.waitKey(100)
    if pressed_key == 27 or pressed_key == ord('q'):
      cv2.destroyAllWindows()
      break
    if cv2.getWindowProperty(window, cv2.WND_PROP_VISIBLE) < 1:
      break
  cv2.destroyAllWindows()


class Graph(metaclass=abc.ABCMeta):
  @abc.abstractmethod
  def show(self):
    pass


class GraphHS:
  def __init__(self, ref_json_filename, cap_json_filename):
    self.__ref_color = ip.colorjson.JsonDeserializer(ref_json_filename)
    self.__cap_color = ip.colorjson.JsonDeserializer(cap_json_filename)
    self.__title = 'HS Error graph'
    self.__xlabel = 'S'
    self.__ylabel = 'H'

    if self.__ref_color.get()['format'] != 'hls' or self.__cap_color.get()['format'] != 'hls':
      raise ValueError('Wrong format, HLS only supported (so far)')

  @staticmethod
  def __get_max_hue():
    return Const.get_max_hue()

  @staticmethod
  def __get_max_saturation():
    return Const.get_max_saturation()

  @staticmethod
  def __get_max_lightness():
    return Const.get_max_lightness()

  def __generate_hs(self):
    img = np.zeros((self.__get_max_hue(), self.__get_max_saturation(), 3), np.uint8)
    height, width, channels = img.shape
    del channels
    img_hls = cv2.cvtColor(img, cv2.COLOR_BGR2HLS)
    lightness = int(self.__get_max_lightness()/2)
    for y in range(0, height):
      for x in range(0, width):
        s_channel, h_channel = x, y
        img_hls[y, x] = [h_channel, lightness, s_channel]
    return img_hls

  def __print_stats(self):
    color_meter = ip.colormeter.ColorMeter(self.__ref_color, self.__cap_color)
    h_perc, l_perc, s_perc = color_meter.get_hls_delta_perc()

    print(Const.Symbols.delta() + 'H [average] : ', round(h_perc, 2), '%', sep='')
    print(Const.Symbols.delta() + 'L [average] : ', round(l_perc, 2), '%', sep='')
    print(Const.Symbols.delta() + 'S [average] : ', round(s_perc, 2), '%', sep='')

  def show(self):
    self.__print_stats()
    img = self.__generate_hs()

    plt.ylim((0, self.__get_max_hue() - 1))
    plt.xlim(0, self.__get_max_saturation() - 1)
    plt.title(self.__title)
    plt.xlabel(self.__xlabel)
    plt.ylabel(self.__ylabel)
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

    ref_point_color = 'bs-'
    cap_point_color = 'ro-'

    for i in range(len(self.__ref_color.get()['channels']['h'])):
      p1_x, p1_y = [
          self.__ref_color.get()['channels']['s'][i],
          self.__ref_color.get()['channels']['h'][i]
      ]

      p2_x, p2_y = [
          self.__cap_color.get()['channels']['s'][i],
          self.__cap_color.get()['channels']['h'][i]
      ]

      plt.plot([p1_x, p2_x], [p1_y, p2_y], color='black', linewidth=0.7)
      plt.plot([p1_x, p1_x], [p1_y, p1_y], ref_point_color)
      plt.plot([p2_x, p2_x], [p2_y, p2_y], cap_point_color)

    ref_legend, = plt.plot([], ref_point_color, label='ref')
    cap_legend, = plt.plot([], cap_point_color, label='cap')

    plt.legend(handles=[ref_legend, cap_legend])
    plt.show()

  @staticmethod
  def create(ref_json_filename, cap_json_filename):
    graph_hs = GraphHS(ref_json_filename, cap_json_filename)
    graph_hs.show()
