#!/usr/bin/env python3
"""Plot generator"""

import numpy as np
import cv2
import ip.colorjson
import ip.colormeter


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

  def __draw_samples(self, img):
    size = len(self.__ref_color.get()['channels']['h'])

    for i in range(0, size):
      cap_channels = self.__ref_color.get()['channels']
      ref_channels = self.__cap_color.get()['channels']

      ref_h, ref_s = ref_channels['h'][i], ref_channels['s'][i]
      cap_h, cap_s = cap_channels['h'][i], cap_channels['s'][i]

      ref_pos = ref_s * self.__scaler, ref_h * self.__scaler
      cap_pos = cap_s * self.__scaler, cap_h * self.__scaler

      ip.draw.Draw.line(img, ref_pos, cap_pos, (0, 0, 0))
      ip.draw.Draw.circle(img, ref_pos, (0, 0, 0))
      ip.draw.Draw.circle(img, cap_pos, (0, 0, 244))

  def get_plot(self):
    img_scaled = cv2.resize(self.__plane, (0, 0), fx=self.__scaler, fy=self.__scaler)
    self.__draw_samples(img_scaled)
    img_math_view = cv2.flip(img_scaled, 0)
    return img_math_view


class GraphGenerator:
  def __init__(self, ref_json_filename, cap_json_filename):
    self.__ref_color = ip.colorjson.ColorJsonParser(ref_json_filename)
    self.__cap_color = ip.colorjson.ColorJsonParser(cap_json_filename)
    if self.__ref_color.get()['format'] != 'hls' or self.__cap_color.get()['format'] != 'hls':
      raise ValueError('Wrong format, HSL only supported (so far)')

  def generate(self):
    window_name = 'window'

    color_meter = ip.colormeter.ColorMeter(self.__ref_color, self.__cap_color)
    h_perc, l_perc, s_perc = color_meter.get_hls_delta_perc()

    print('\u0394H :', round(h_perc, 2), '%')
    print('\u0394L :', round(l_perc, 2), '%')
    print('\u0394S :', round(s_perc, 2), '%')

    hs_plane = PlaneHS(self.__ref_color, self.__cap_color, 3)
    img = hs_plane.get_plot()
    cv2.imshow(window_name, img)

    while True:
      pressedkey = cv2.waitKey(100)
      if pressedkey == 27 or pressedkey == ord('q'):
        cv2.destroyAllWindows()
        break
      if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
        break
    cv2.destroyAllWindows()

  @staticmethod
  def create(ref_json_filename, cap_json_filename):
    graph_generator = GraphGenerator(ref_json_filename, cap_json_filename)
    graph_generator.generate()
