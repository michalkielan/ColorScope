import cv2
import numpy as np
import json
import sys

def get_plot_scaler(): return 3

def draw_circle(window, pos, bgr):
  circle_rad = 6
  cv2.circle(window, pos, circle_rad, bgr, -1)
  cv2.circle(window, pos, circle_rad, (0, 0, 0), 1)

def draw_line(img, start_pos, end_pos, bgr):
  cv2.line(img, start_pos, end_pos, bgr, thickness=1, lineType=8, shift=0)

def draw_rect(window, pos, bgr):
  circle_rad = 3
  cv2.circle(window, pos, circle_rad, bgr, -1)
  cv2.circle(window, pos, circle_rad, (0, 0, 0), 1)

def gen_hv_plane():
  img = np.zeros((180, 255, 3), np.uint8)
  height, width, channels = img.shape
  print(width, height)
  img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HLS)
  for y in range(0, height):
    for x in range(0, width):
      s = x
      h = y
      img_hsv[y, x] = [h, 128, s]
  return img_hsv

def draw_samples(plane, ref, cap):
  size = min(len(ref), len(cap))
  for i in range(0, size):
    ref_h, ref_s = ref[i][0]*get_plot_scaler(), ref[i][2]*get_plot_scaler()
    cap_h, cap_s = cap[i][0]*get_plot_scaler(), cap[i][2]*get_plot_scaler()
    ref_pos = ref_s, ref_h
    cap_pos = cap_s, cap_h
    draw_line(plane, ref_pos, cap_pos, (0, 0, 0))
    draw_circle(plane, ref_pos, (0, 0, 0))
    draw_circle(plane, cap_pos, (0, 0, 244))

class ColorJsonParser:
  def __init__(self, json_filename):
    if not os.path.exists(json_filename):
      raise FileNotFoundError('Json file :' + json_filename + ' not found')

    with open(json_filename) as color_file:
      self.__color_data = json.load(color_file)

  def get():
    return self.__color_data

def get_json_data(color_json_filename):
  with open(color_json_filename) as color_file:
    color_data = json.load(color_file)
    return color_data

def calc_saturation(ref_color_json_filename, cap_color_json_filename):
  ref_color_data = get_json_data(ref_color_json_filename)
  cap_color_data = get_json_data(cap_color_json_filename)

  if ref_color_data['format'] != 'hls' or cap_color_data['format'] != 'hls':
    raise AttributeError('Color not HLS type')

  ref_h, cap_h = ref_color_data['channels']['h'], cap_color_data['channels']['h']
  ref_l, cap_l = ref_color_data['channels']['l'], cap_color_data['channels']['l']
  ref_s, cap_s = ref_color_data['channels']['s'], cap_color_data['channels']['s']

  delta_perc  = lambda ref, cap : (cap * 100.0) / ref 

  delta_h_perc_data = [delta_perc(ref, cap) for ref, cap in zip(ref_h, cap_h)]
  delta_l_perc_data = [delta_perc(ref, cap) for ref, cap in zip(ref_l, cap_l)]
  delta_s_perc_data = [delta_perc(ref, cap) for ref, cap in zip(ref_s, cap_s)]
  
  delta_h_perc, delta_s_perc, delta_l_perc = [
      np.average(delta_h_perc_data),
      np.average(delta_l_perc_data),
      np.average(delta_s_perc_data)
  ]

  print('\u0394H :', round(delta_h_perc, 2), '%')
  print('\u0394L :', round(delta_l_perc, 2), '%')
  print('\u0394S :', round(delta_s_perc, 2), '%')


calc_saturation('ref_data.json', 'cap_data.json')
sys.exit(0)
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
  if cv2.getWindowProperty('window', cv2.WND_PROP_VISIBLE) < 1:
    break
cv2.destroyAllWindows()
