import cv2
import os
import numpy as np
import json
import sys


class Draw:
  @staticmethod
  def circle(img, pos, bgr):
    circle_rad = 6
    cv2.circle(img, pos, circle_rad, bgr, -1)
    cv2.circle(img, pos, circle_rad, (0, 0, 0), 1)
  
  @staticmethod
  def line(img, p1, p2, bgr):
    cv2.line(img, p1, p2, bgr, thickness=1, lineType=8, shift=0)
  
  @staticmethod
  def rect(img, pos, bgr):
    circle_rad = 3
    cv2.circle(img, pos, circle_rad, bgr, -1)
    cv2.circle(img, pos, circle_rad, (0, 0, 0), 1)


class ColorJsonParser:
  def __init__(self, json_filename):
    if not os.path.exists(json_filename):
      raise FileNotFoundError('Json file :' + json_filename + ' not found')

    with open(json_filename) as color_file:
      self.__color_data = json.load(color_file)

  def get(self):
    return self.__color_data

def get_json_data(color_json_filename):
  with open(color_json_filename) as color_file:
    color_data = json.load(color_file)
    return color_data


class PlaneHS:
  def __init__(self, ref_color_data, cap_color_data, scaler):
    self.__ref_color = ref_color_data
    self.__cap_color = cap_color_data
    self.__scaler = scaler
    self.__plane = self.__generateHS()

  @staticmethod
  def __generateHS():
    img = np.zeros((180, 255, 3), np.uint8)
    height, width, channels = img.shape
    img_hls = cv2.cvtColor(img, cv2.COLOR_BGR2HLS)
    for y in range(0, height):
      for x in range(0, width):
        s, h = x, y
        img_hls[y, x] = [h, 128, s]
    return img_hls
  
  def __draw_samples(self, img):
    size = len(self.__ref_color.get()['channels']['h'])
    
    for i in range(0, size):
      ref_h = self.__ref_color.get()['channels']['h'][i]
      ref_s = self.__ref_color.get()['channels']['s'][i]
      
      cap_h = self.__cap_color.get()['channels']['h'][i]
      cap_s = self.__cap_color.get()['channels']['s'][i]
       
      ref_pos = ref_s * self.__scaler, ref_h * self.__scaler
      cap_pos = cap_s * self.__scaler, cap_h * self.__scaler

      Draw.line(img, ref_pos, cap_pos, (0, 0, 0))
      Draw.circle(img, ref_pos, (0, 0, 0))
      Draw.circle(img, cap_pos, (0, 0, 244))

  def get_plot(self):
    img_scaled = cv2.resize(self.__plane, (0,0), fx=self.__scaler, fy=self.__scaler)
    self.__draw_samples(img_scaled)
    img_math_view = cv2.flip(img_scaled, 0)
    return img_math_view
    

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
  
    delta_perc  = lambda ref, cap : (cap * 100.0) / ref 
  
    delta_h_perc_data = [delta_perc(ref, cap) for ref, cap in zip(ref_h, cap_h)]
    delta_l_perc_data = [delta_perc(ref, cap) for ref, cap in zip(ref_l, cap_l)]
    delta_s_perc_data = [delta_perc(ref, cap) for ref, cap in zip(ref_s, cap_s)]
    
    return [
        np.average(delta_h_perc_data),
        np.average(delta_l_perc_data),
        np.average(delta_s_perc_data)
    ]

ref_color = ColorJsonParser('ref.json')
cap_color = ColorJsonParser('cap.json')

color_meter = ColorMeter(ref_color, cap_color)
h_perc, l_perc, s_perc = color_meter.get_hls_delta_perc()

print('\u0394H :', round(h_perc, 2), '%')
print('\u0394L :', round(l_perc, 2), '%')
print('\u0394S :', round(s_perc, 2), '%')

window_name = 'window'
hs_plane = PlaneHS(ref_color, cap_color, 3)
img = hs_plane.get_plot()
cv2.imshow(window_name, img)


#plane = gen_hv_plane()
#big = cv2.resize(plane, (0,0), fx=get_plot_scaler(), fy=get_plot_scaler())
#draw_samples(big, ref, cap)
#math_axis_img = cv2.flip(big, 0)
#cv2.imshow('window', math_axis_img)

while True:
  pressedkey = cv2.waitKey(100)
  if pressedkey == 27 or pressedkey == ord('q'):
    cv2.destroyAllWindows()
    break
  if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
    break
cv2.destroyAllWindows()
