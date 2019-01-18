#!/usr/bin/env python3.5
"""Script to read the rgb color of each pixel"""

import sys
import cv2

class ImageProcessing:
  def __init__(self, filename):
    self.filename = filename
    self.img = cv2.imread(self.filename)

  def __read_colors__(self, pos):
    pos_x, pos_y = pos
    color = self.img[pos_y, pos_x, :]
    val_b, val_g, val_r = color
    print(val_r, '\t', val_g, '\t', val_b)

  def __mouse_event_processing__(self, pos):
    self.__read_colors__(pos)

  def on_mouse_event(self, event, pos_x, pos_y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
      self.__mouse_event_processing__((pos_x, pos_y))

  def processing(self):
    cv2.imshow(self.filename, self.img)

    cv2.setMouseCallback(self.filename, self.on_mouse_event)
    pressedkey = cv2.waitKey(0)

    if pressedkey == 27:
      cv2.destroyAllWindows()

def main():
  if len(sys.argv) < 2:
    print('Specify image name: ./pixel_clicker.py image_file.jpg')
  else:
    img_filename = sys.argv[1]
    print('Filename: ', img_filename)
    img = ImageProcessing(img_filename)
    img.processing()

if __name__ == '__main__':
  main()
