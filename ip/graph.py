#!/usr/bin/env python3
"""Plot generator"""

import numpy as np
import cv2
import ip.colorjson
import ip.colormeter
import matplotlib.pyplot as plt


class Const:
  @staticmethod
  def ref_color():
    return (0, 0, 0)

  @staticmethod
  def cap_color():
    return (0, 0, 244)

  class Symbols:
    @staticmethod
    def delta():
      return '\u0394'

def show_window(window_name):
  while True:
    pressed_key = cv2.waitKey(100)
    if pressed_key == 27 or pressed_key == ord('q'):
      cv2.destroyAllWindows()
      break
    if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
      break
  cv2.destroyAllWindows()


class Plotter():
  pass


class PlotterHS():
  pass


class PlotterLum():
  pass


class PlaneHS:
  def __init__(self, ref_color_data, cap_color_data, scaler):
    self.__ref_color = ref_color_data
    self.__cap_color = cap_color_data
    self.__scaler = scaler
    self.__plane = self.__generate_hs()

  @staticmethod
  def __generate_hs():
    max_hue = 180
    max_sat = 255
    img = np.zeros((max_hue, max_sat, 3), np.uint8)
    height, width, channels = img.shape
    del channels
    img_hls = cv2.cvtColor(img, cv2.COLOR_BGR2HLS)
    for y in range(0, height):
      for x in range(0, width):
        s_channel, h_channel = x, y
        img_hls[y, x] = [h_channel, 128, s_channel]
    return img_hls

  def get_plot(self):
     return self.__plane


class GraphGenerator:
  def __init__(self, ref_json_filename, cap_json_filename):
    self.__ref_color = ip.colorjson.ColorJsonParser(ref_json_filename)
    self.__cap_color = ip.colorjson.ColorJsonParser(cap_json_filename)
    if self.__ref_color.get()['format'] != 'hls' or self.__cap_color.get()['format'] != 'hls':
      raise ValueError('Wrong format, HSL only supported (so far)')

  @staticmethod
  def __label_x(img, pos, text):
    ip.draw.Draw.put_text(img, pos, text, 0.3)

  @staticmethod
  def __label_y(img, pos, text):
    ip.draw.Draw.put_text(img, pos, text, 0.3)

  def generate_hs(self):
    window_name = 'HS error graph'

    color_meter = ip.colormeter.ColorMeter(self.__ref_color, self.__cap_color)
    h_perc, l_perc, s_perc = color_meter.get_hls_delta_perc()

    print(Const.Symbols.delta() + 'H [average] : ', round(h_perc, 2), '%', sep='')
    print(Const.Symbols.delta() + 'L [average] : ', round(l_perc, 2), '%', sep='')
    print(Const.Symbols.delta() + 'S [average] : ', round(s_perc, 2), '%', sep='')

    hs_plane = PlaneHS(self.__ref_color, self.__cap_color, 1)
    img = hs_plane.get_plot()

    img_graph = img

    plt.ylim((0, 179))
    plt.xlim(0, 254)

    plt.title('HS error graph')
    plt.xlabel('Saturation')
    plt.ylabel('Hue')

    plt.imshow(cv2.cvtColor(img_graph, cv2.COLOR_BGR2RGB))
    plt.gca().invert_yaxis()

    size = len(self.__ref_color.get()['channels']['h'])

    for i in range(0, size):
      ref_channels = self.__ref_color.get()['channels']
      cap_channels = self.__cap_color.get()['channels']

      ref_x = ref_channels['s'][i]
      ref_y = ref_channels['h'][i]

      cap_x = cap_channels['s'][i]
      cap_y = cap_channels['h'][i]

      plt.plot([ref_x, cap_x], [ref_y, cap_y], color='black', linewidth=0.7)
      plt.plot([ref_x, ref_x], [ref_y, ref_y], 'bs-')
      plt.plot([cap_x, cap_x], [cap_y, cap_y], 'ro-')

    plt.show()

  @staticmethod
  def create(ref_json_filename, cap_json_filename):
    graph_generator = GraphGenerator(ref_json_filename, cap_json_filename)
    graph_generator.generate_hs()
