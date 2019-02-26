#!/usr/bin/env python3
"""Quality measurement"""
import abc
from enum import IntEnum
import numpy as np
from skimage.measure import compare_ssim as ssim


class ChannelsRGB(IntEnum):
  red = 2
  green = 1
  blue = 0


class ChannelsYUV(IntEnum):
  Y = 0
  U = 1
  V = 2


class  QualityMeasurement(metaclass=abc.ABCMeta):
  @staticmethod
  def create(img_loader_ref, img_loader_cap, measurement_method=''):
    if measurement_method == 'ssim-sc':
      return QualityMeasurementSSIMsingleChannel(img_loader_ref, img_loader_cap)
    if measurement_method == 'ssim':
      return QualityMeasurementSSIM(img_loader_ref, img_loader_cap)
    if measurement_method == 'psnr':
      return QualityMeasurementPSNR(img_loader_ref, img_loader_cap)
    if measurement_method == 'psnr-sc':
      return QualityMeasurementPSNRsingleChannel(img_loader_ref, img_loader_cap)
    raise AttributeError('quality_measure_factory method {} not found'.format(measurement_method))

  def __init__(self, img_loader_ref, img_loader_cap):
    self._image_ref = img_loader_ref.get_native_channels()
    self._image_cap = img_loader_cap.get_native_channels()
    if self._image_ref is None or self._image_cap is None:
      raise AttributeError('Incorrect input data files')
    if self._image_ref.shape != self._image_cap.shape:
      raise AttributeError('Unmatching images size')


class QualityMeasurementPSNRsingleChannel(QualityMeasurement):
  def __init__(self, img_loader_ref, img_loader_cap):
    QualityMeasurement.__init__(self, img_loader_ref, img_loader_cap)

  def process(self, chan_no):
    i_mat = self._image_ref[:, :, chan_no].astype(float)
    k_mat = self._image_cap[:, :, chan_no].astype(float)
    mean_square_error = (np.square(i_mat-k_mat)).mean()
    channel_max_value = 255
    if mean_square_error == 0:
      return np.inf
    return 10 * np.log10((np.square(channel_max_value))/mean_square_error)


class QualityMeasurementSSIMsingleChannel(QualityMeasurement):
  def __init__(self, img_loader_ref, img_loader_cap):
    QualityMeasurement.__init__(self, img_loader_ref, img_loader_cap)

  def process(self, ch_no):
    i_mat = self._image_ref[:, :, ch_no]
    k_mat = self._image_cap[:, :, ch_no]
    return ssim(i_mat, k_mat)


class QualityMeasurementSSIM(QualityMeasurement):
  def __init__(self, img_loader_ref, img_loader_cap):
    QualityMeasurement.__init__(self, img_loader_ref, img_loader_cap)

  def process(self):
    i_mat = self._image_ref
    k_mat = self._image_cap
    return ssim(i_mat, k_mat, multichannel=True)


class QualityMeasurementPSNR(QualityMeasurement):
  def __init__(self, img_loader_ref, img_loader_cap):
    QualityMeasurement.__init__(self, img_loader_ref, img_loader_cap)

  def process(self):
    i_mat = self._image_ref.astype(float)
    k_mat = self._image_cap.astype(float)
    mean_square_error = np.sum(np.square(i_mat - k_mat))/float(i_mat.shape[0]*i_mat.shape[1])/3.0
    if mean_square_error == 0:
      return np.inf
    channel_max_value = 255
    return 10 * np.log10((np.square(channel_max_value))/mean_square_error)
