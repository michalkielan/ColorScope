#!/usr/bin/env python3.5
import cv2
import sys


class ImageProcessing:
  def __init__(self, filename):
    self.filename = filename

  def __readColors__(self, x, y):
    color = self.img[y, x, :]
    b, g, r = color
    print(r, '\t', g, '\t', b)

  def __mouseEventProcessing__(self, x, y):
    self.__readColors__(x, y)

  def onMouseEvent(self, event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
       self.__mouseEventProcessing__(x, y)

  def processing(self):
    self.img = cv2.imread(self.filename)
    cv2.imshow(self.filename, self.img)

    cv2.setMouseCallback(self.filename, self.onMouseEvent)
    self.pressedkey = cv2.waitKey(0)

    if self.pressedkey == 27:
        cv2.destroyAllWindows()


if __name__ =='__main__':
  if len(sys.argv) < 2:
    print('Specify image name: ./PixelClicker.py image_file.jpg')
  else:
    filename = sys.argv[1]
    print('Filename: ', filename)
    img = ImageProcessing(filename)
    img.processing()
