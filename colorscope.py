#!/usr/bin/env python3
"""Script to read the color values"""

import argparse
import sys
import os
import ip.imgloader
import ip.colorjson
import ip.colorreader
import ip.graph
import ip.qualitymeasurement

class ColorArgumentParser:
  @staticmethod
  def parse_video_size_arg(video_size):
    if video_size != '':
      w, h = video_size.split('x', 1)
      return int(w), int(h)
    return None

  @staticmethod
  def is_metric_name_correct(given_metrics):
    list_of_metrics_names = ["ssim", "psnr"]

    if given_metrics in list_of_metrics_names:
      return True
    return False

  def process_mulitchannel_compare(self, multichannel_args):
    if len(multichannel_args) == 7:
      [metric,
       ref_img_dir, ref_pxl_fmt, ref_vd_sz,
       cap_img_dir, cap_pxl_fmt, cap_vd_sz] = multichannel_args

    elif len(multichannel_args) == 3:
      [metric, ref_img_dir, cap_img_dir] = multichannel_args
      ref_pxl_fmt = ref_vd_sz = cap_pxl_fmt = cap_vd_sz = ''

    else:
      return (False, 0.0)

    video_size_ref = self.parse_video_size_arg(ref_vd_sz)
    video_size_cap = self.parse_video_size_arg(cap_vd_sz)
    img_load_ref = ip.imgloader.create(ref_img_dir, ref_pxl_fmt, video_size_ref)
    img_load_cap = ip.imgloader.create(cap_img_dir, cap_pxl_fmt, video_size_cap)

    if not self.is_metric_name_correct(metric):
      return (False, 0.0)

    return(True,
           ip.qualitymeasurement.QualityMeasurement.
           create(img_load_ref, img_load_cap, metric).process()
          )

  def process_singlechannel_compare(self, singlechannel_args):
    if len(singlechannel_args) == 8:
      [metric, channel_no,
       ref_img_dir, ref_pxl_fmt, ref_vd_sz,
       cap_img_dir, cap_pxl_fmt, cap_vd_sz] = singlechannel_args

    elif len(singlechannel_args) == 4:
      [metric, channel_no, ref_img_dir, cap_img_dir] = singlechannel_args
      ref_pxl_fmt = ref_vd_sz = cap_pxl_fmt = cap_vd_sz = ''

    else:
      return (False, 0.0)

    video_size_ref = self.parse_video_size_arg(ref_vd_sz)
    video_size_cap = self.parse_video_size_arg(cap_vd_sz)
    img_load_ref = ip.imgloader.create(ref_img_dir, ref_pxl_fmt, video_size_ref)
    img_load_cap = ip.imgloader.create(cap_img_dir, cap_pxl_fmt, video_size_cap)

    if not self.is_metric_name_correct(metric):
      return (False, 0.0)

    return(True,
           ip.qualitymeasurement.QualityMeasurement.
           create(img_load_ref, img_load_cap, metric + "-sc").process(int(channel_no))
          )

  def __init__(self):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i',
        '--imgfile',
        type=str,
        help='Image file',
        default=''
    )

    parser.add_argument(
        '-o',
        '--out',
        type=str,
        help='Json file',
        default='color_data.json'
    )

    parser.add_argument(
        '-pix_fmt',
        '--pixel_format',
        type=str, help='Raw input pixel format: nv21, nv12',
        default=''
    )

    parser.add_argument(
        '-s',
        '--video_size',
        type=str, help='WxH set the frame size',
        default=''
    )

    parser.add_argument(
        '-out_fmt',
        '--output_format',
        type=str,
        help='Output rgb, yuv, hsv, hls (Default: rgb)',
        default='rgb'
    )

    parser.add_argument(
        '-flt',
        '--filter',
        type=str,
        help='Output med, avg (Default: avg)',
        default='avg'
    )

    parser.add_argument(
        '-gen',
        '--gen_graph',
        type=str,
        help='gen_graph ref.json cap.json Generate graphs',
        nargs=2,
        default=''
    )

    parser.add_argument(
        '-cp',
        '--compare',
        type=str,
        nargs='+',
        help='compare two images using given metrics'
    )

    parser.add_argument(
        '-scp',
        '--compare_singlechannel',
        type=str,
        nargs='+',
        help='compare two images using given metrics for given channel'
    )

    args = parser.parse_args()
    pixel_format = args.pixel_format.lower()
    video_size = self.parse_video_size_arg(args.video_size)

    if args.compare:
      result, metric_value = self.process_mulitchannel_compare(args.compare)
      if result is True:
        print(metric_value)
        sys.exit(0)
      sys.exit('Compare finished unsucessfuly for given metric.')

    if args.compare_singlechannel:
      result, metric_value = self.process_singlechannel_compare(args.compare_singlechannel)
      if result is True:
        print(metric_value)
        sys.exit(0)
      sys.exit('Compare finished unsucessfuly for given metric.')

    if args.gen_graphs != '':
      ref_json, cap_json = args.gen_graphs
      try:
        ip.graph.GraphHS.create(ref_json, cap_json)
      except (AttributeError, ValueError) as err:
        err = sys.exc_info()[1]
        sys.exit('Cannot generate graph: ' + str(err))
      sys.exit(0)

    if not os.path.exists(args.img_file):
      sys.exit('File not found')

    image_loader = ip.imgloader.create(args.img_file, pixel_format, video_size)

    try:
      output_format = args.output_format.lower()
      filter_type = args.filter.lower()

      color_reader = ip.colorreader.create(
          output_format,
          image_loader,
          filter_type,
          args.out
      )
      color_reader.processing()
    except (AttributeError, ValueError) as err:
      err = sys.exc_info()[1]
      sys.exit('Cannot read image: ' + str(err))


def main():
  ColorArgumentParser()


if __name__ == '__main__':
  main()
