import cv2
import numpy as np

def get_plot_scaler(): return 3

ref = [ 
[155,  46,   84],
[173,  120,  106],
[112,  101,  184],
[56,   35,   101],
[128,  113,  151],
[87,   102,  187],
[8,    128,  210],
[117,  119,  216],
[177,  117,  194],
[136,  40,   191],
[42,   108,  214],
[14,   139,  230],
[118,  99,   230],
[67,   68,   204],
[1,    104,  221],
[24,   136,  245],
[163,  122,  211],
[105,  94,   242]
]

cap = [
[154,  3,    136],
[171,  115,  127],
[113,  92,   209],
[55,   25,   195],
[130,  106,  187],
[83,   110,  207],
[7,    121,  235],
[120,  111,  246],
[175,  108,  244],
[135,  24,   255],
[43,   119,  241],
[14,   136,  254],
[120,  87,   255],
[64,   70,   246],
[0,    92,   255],
[25,   136,  255],
[161,  110,  255],
[105,  85,   255]
]
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

plane = gen_hv_plane()
big = cv2.resize(plane, (0,0), fx=get_plot_scaler(), fy=get_plot_scaler())
draw_samples(big, ref, cap)
math_axis_img = cv2.flip(big, 0)
cv2.imshow('window', math_axis_img)

while True:
  pressedkey = cv2.waitKey(100)
  if pressedkey == 27 or pressedkey == ord('q'):
    cv2.destroyAllWindows()
    break
  if cv2.getWindowProperty('window', cv2.WND_PROP_VISIBLE) < 1:
    break
cv2.destroyAllWindows()
