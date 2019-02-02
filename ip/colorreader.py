#!/rusr/bin/env python3
"""Read color values"""

import abc
import cv2
import ip.colorfilter
import ip.colorjson
import ip.draw
import ip.graph


class ColorReader(metaclass=abc.ABCMeta):
  def __init__(self, image_loader, filter_type):
    rect_color = (0, 0, 255)
    self.__window = 'ColorScope'
    self._img = image_loader.imread()
    self._filter = ip.colorfilter.create(filter_type)
    if self._img is None:
      raise AttributeError('ColorReader.__init__: image load failed')

    self._img_mark = self._img.copy()
    self.__drawer = ip.draw.RectDrawer(self.__window, self._img, rect_color)
    self.__rect = [[0, 0], [0, 0]]
    self._color_json = None

  @abc.abstractmethod
  def _get_color_format(self, img_roi):
    pass

  def read_rect_color(self, rect):
    p1_x, p1_y = [rect[0][0], rect[0][1]]
    p2_x, p2_y = [rect[1][0], rect[1][1]]

    min_x, min_y = [min(p1_x, p2_x), min(p1_y, p2_y)]
    max_x, max_y = [max(p1_x, p2_x), max(p1_y, p2_y)]

    roi = self._img[min_y:max_y, min_x:max_x]

    return self._filter.filter(self._get_color_format(roi))

  def __on_mouse_event(self, event, x, y, flags, param):
    del flags, param
    if event == cv2.EVENT_LBUTTONDOWN:
      self.__drawer.start((x, y))
      self.__rect[0] = [x, y]

    elif event == cv2.EVENT_MOUSEMOVE:
      self.__drawer.draw((x, y))

    elif event == cv2.EVENT_LBUTTONUP:
      self.__drawer.end((x, y))
      self.__rect[1] = [x, y]
      if self.__rect[0] != self.__rect[1]:
        color = self.read_rect_color(self.__rect)
        self._color_json.append(color)
        print('\t'.join(map(str, color)))

  def processing(self):
    cv2.imshow(self.__window, self._img)
    cv2.setMouseCallback(self.__window, self.__on_mouse_event)
    ip.graph.show_window(self.__window)
    self._color_json.write()

  @staticmethod
  def create(color_format, image_loader, filter_type, out_json_filename):
    if color_format == 'rgb':
      return ColorReaderRGB(image_loader, out_json_filename, filter_type)
    if color_format == 'yuv':
      return ColorReaderYUV(image_loader, out_json_filename, filter_type)
    if color_format == 'hsv':
      return ColorReaderHSV(image_loader, out_json_filename, filter_type)
    if color_format == 'hls':
      return ColorReaderHLS(image_loader, out_json_filename, filter_type)
    raise AttributeError('make_color_reader: ' + color_format + ' not found')


class ColorReaderRGB(ColorReader):
  def __init__(self, filename, json_filename, filter_type='avg'):
    super().__init__(filename, filter_type)
    self._color_json = ip.colorjson.JsonSerializerRGB(json_filename)
    print('R', 'G', 'B', sep='\t')

  def _get_color_format(self, img_roi):
    return cv2.cvtColor(img_roi, cv2.COLOR_BGR2RGB)


class ColorReaderYUV(ColorReader):
  def __init__(self, filename, json_filename, filter_type='avg'):
    super().__init__(filename, filter_type)
    self._color_json = ip.colorjson.JsonSerializerYUV(json_filename)
    print('Y', 'U', 'V', sep='\t')

  def _get_color_format(self, img_roi):
    return cv2.cvtColor(img_roi, cv2.COLOR_BGR2YUV)


class ColorReaderHSV(ColorReader):
  def __init__(self, filename, json_filename, filter_type='avg'):
    super().__init__(filename, filter_type)
    self._color_json = ip.colorjson.JsonSerializerHSV(json_filename)
    print('H', 'S', 'V', sep='\t')

  def _get_color_format(self, img_roi):
    return cv2.cvtColor(img_roi, cv2.COLOR_BGR2HSV)


class ColorReaderHLS(ColorReader):
  def __init__(self, filename, json_filename, filter_type='avg'):
    super().__init__(filename, filter_type)
    self._color_json = ip.colorjson.JsonSerializerHLS(json_filename)
    print('H', 'L', 'S', sep='\t')

  def _get_color_format(self, img_roi):
    return cv2.cvtColor(img_roi, cv2.COLOR_BGR2HLS)


def create(color_format, img_loader, filter_type, out_json_filename):
  return ColorReader.create(
      color_format,
      img_loader,
      filter_type,
      out_json_filename
  )
