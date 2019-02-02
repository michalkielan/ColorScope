#!/usr/bin/env python3
"""Script to parse json"""

import os
import json
import abc


class JsonSerializer(metaclass=abc.ABCMeta):
  def __init__(self, filename):
    self.__filename = filename
    self._color_data = {}

  def append(self, color):
    length = len(color)
    if length != len(self._color_data['format']):
      raise ValueError('Number of channels not match')

    for i in range(0, length):
      channel = self._color_data['format'][i]
      self._color_data['channels'][channel].append(color[i])

  def write(self):
    with open(self.__filename, 'w') as outfile:
      json.dump(self._color_data, outfile)


class JsonSerializerRGB(JsonSerializer):
  def __init__(self, filename):
    super().__init__(filename)
    self._color_data = {
        'format': 'rgb', 'channels': {'r': [], 'g': [], 'b': []}
    }


class JsonSerializerYUV(JsonSerializer):
  def __init__(self, filename):
    super().__init__(filename)
    self._color_data = {
        'format': 'yuv', 'channels': {'y': [], 'u': [], 'v': []}
    }


class JsonSerializerHSV(JsonSerializer):
  def __init__(self, filename):
    super().__init__(filename)
    self._color_data = {
        'format': 'hsv', 'channels': {'h': [], 's': [], 'v': []}
    }


class JsonSerializerHLS(JsonSerializer):
  def __init__(self, filename):
    super().__init__(filename)
    self._color_data = {
        'format': 'hls', 'channels': {'h': [], 'l': [], 's': []}
    }


class JsonDeserializer:
  def __init__(self, json_filename):
    if not os.path.exists(json_filename):
      raise FileNotFoundError('Json file :' + json_filename + ' not found')

    with open(json_filename) as color_file:
      self.__color_data = json.load(color_file)

  def get(self):
    return self.__color_data
