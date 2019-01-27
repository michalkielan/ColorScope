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
