import cv2
import numpy as np

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
  img = np.zeros((255, 255, 3), np.uint8)
  h, w, channels = img.shape
  img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
  for y in range(0, h):
    for x in range(0, w):
      s = x
      v = y
      img_hsv[y, x] = [125, s, v]
  return img_hsv

plane = gen_hv_plane()

ref = [ 
[155,	84,	46],
[173,	106,	120],
[112,	184,	101],
[56,	101,	35],
[128,	151,	113],
[87,	187,	102],
[8,	210,	128],
[117,	216,	119],
[177,	194,	117],
[136,	191,	40],
[42,	214,	108],
[14,	230,	139],
[118,	230,	99],
[67,	204,	68],
[1,	221,	104],
[24,	245,	136],
[163,	211,	122],
[105,	242,	94]]

cap = [
[154,	136,	32],
[171,	127,	115],
[113,	209,	92],
[55,	195,	25],
[130,	187,	106],
[83,	207,	110],
[7,	235,	121],
[120,	246,	111],
[175,	244,	108],
[135,	255,	24],
[43,	241,	119],
[14,	254,	136],
[120,	255,	87],
[64,	246,	70],
[0,	255,	92],
[25,	255,	136],
[161,	255,	110],
[105,	255,    85]]

def draw_circles(plane, ref, cap):
  size = min(len(ref), len(cap))
  for i in range(0, size):
    ref_s, ref_v = ref[i][1]*2, ref[i][2]*2
    cap_s, cap_v = cap[i][1]*2, cap[i][2]*2
    ref_pos = ref_s, ref_v
    cap_pos = cap_s, cap_v
    draw_circle(plane, ref_pos, (0, 0, 0))
    draw_circle(plane, cap_pos, (0, 0, 244))
    draw_line(plane, ref_pos, cap_pos, (0, 0, 0))

big = cv2.resize(plane, (0,0), fx=2, fy=2)

draw_circles(big, ref, cap)


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
