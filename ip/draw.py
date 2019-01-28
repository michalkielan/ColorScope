#!/usr/bin/env python3
"""Drawing helpers"""

import cv2


class RectDrawer:
  def __init__(self, window, image, color):
    self.__is_draw = False
    self.__start_pos = [0, 0]
    self.__color = color
    self.__window = window
    self.__img = image
    self.__img_mark = self.__img.copy()

  def start(self, pos):
    self.__is_draw = True
    self.__start_pos = pos

  def draw(self, pos):
    if self.__is_draw:
      self.__img = self.__img_mark.copy()
      cv2.rectangle(self.__img, self.__start_pos, pos, self.__color, 1)
      cv2.imshow(self.__window, self.__img)

  def end(self, pos):
    self.__is_draw = False
    cv2.rectangle(self.__img, self.__start_pos, pos, self.__color, 1)
    cv2.imshow(self.__window, self.__img)


class Draw:
  @staticmethod
  def circle(img, pos, bgr):
    circle_rad = 6
    cv2.circle(img, pos, circle_rad, bgr, -1)
    cv2.circle(img, pos, circle_rad, (0, 0, 0), 1)

  @staticmethod
  def line(img, point1, point2, bgr):
    cv2.line(img, point1, point2, bgr, thickness=1, lineType=8, shift=0)

  @staticmethod
  def rect(img, pos, bgr):
    circle_rad = 3
    cv2.circle(img, pos, circle_rad, bgr, -1)
    cv2.circle(img, pos, circle_rad, (0, 0, 0), 1)
