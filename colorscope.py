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
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements

def parse_video_size_arg(video_size):
  if video_size != '':
    w, h = video_size.split('x', 1)
    return int(w), int(h)
  return None


def is_metric_name_correct(given_metrics):
  list_of_metrics_names = ["ssim", "psnr"]
  if given_metrics in list_of_metrics_names:
    return True
  return False

def process_mulitchannel_compare(multichannel_args):
  if len(multichannel_args) == 7:
    [metric,
     ref_img_dir, ref_pxl_fmt, ref_vd_sz,
     cap_img_dir, cap_pxl_fmt, cap_vd_sz] = multichannel_args
  elif len(multichannel_args) == 3:
    [metric, ref_img_dir, cap_img_dir] = multichannel_args
    ref_pxl_fmt = ref_vd_sz = cap_pxl_fmt = cap_vd_sz = ''
  else:
    return (False, 0.0)
  video_size_ref = parse_video_size_arg(ref_vd_sz)
  video_size_cap = parse_video_size_arg(cap_vd_sz)
  img_load_ref = ip.imgloader.create(ref_img_dir, ref_pxl_fmt, video_size_ref)
  img_load_cap = ip.imgloader.create(cap_img_dir, cap_pxl_fmt, video_size_cap)
  if not is_metric_name_correct(metric):
    return (False, 0.0)
  return(True,
         ip.qualitymeasurement.QualityMeasurement.
         create(img_load_ref, img_load_cap, metric).process())


def process_singlechannel_compare(singlechannel_args):
  if len(singlechannel_args) == 8:
    [metric, channel_no,
     ref_img_dir, ref_pxl_fmt, ref_vd_sz,
     cap_img_dir, cap_pxl_fmt, cap_vd_sz] = singlechannel_args
  elif len(singlechannel_args) == 4:
    [metric, channel_no, ref_img_dir, cap_img_dir] = singlechannel_args
    ref_pxl_fmt = ref_vd_sz = cap_pxl_fmt = cap_vd_sz = ''
  else:
    return (False, 0.0)
  video_size_ref = parse_video_size_arg(ref_vd_sz)
  video_size_cap = parse_video_size_arg(cap_vd_sz)
  img_load_ref = ip.imgloader.create(ref_img_dir, ref_pxl_fmt, video_size_ref)
  img_load_cap = ip.imgloader.create(cap_img_dir, cap_pxl_fmt, video_size_cap)
  if not is_metric_name_correct(metric):
    return (False, 0.0)
  return(True,
         ip.qualitymeasurement.QualityMeasurement.
         create(img_load_ref, img_load_cap, metric + "-sc").process(int(channel_no)))


def main():
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
      #nargs=7,
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
  output_format = args.output_format.lower()
  video_size = parse_video_size_arg(args.video_size)
  filter_type = args.filter.lower()

  img_file = args.imgfile
  out_json_file = args.out
  gen_graph_filenames = args.gen_graph
  compare_multichannel = args.compare
  compare_singlechannel = args.compare_singlechannel

  #colorscope -compare metrics [channelId] refImageDir [ref_pixel_format] \
  #[ref_video_size] capImageDir [cap_pixel_format] [cap_video_size]
  if compare_multichannel:
    result, metric_value = process_mulitchannel_compare(compare_multichannel)
    if result is True:
      print(metric_value)
      sys.exit(0)
    sys.exit('Compare finished unsucessfuly for given metric.')

  if compare_singlechannel:
    result, metric_value = process_singlechannel_compare(compare_singlechannel)
    if result is True:
      print(metric_value)
      sys.exit(0)
    sys.exit('Compare finished unsucessfuly for given metric.')

  if gen_graph_filenames != '':
    ref_json, cap_json = gen_graph_filenames
    try:
      ip.graph.GraphHS.create(ref_json, cap_json)
    except (AttributeError, ValueError) as err:
      err = sys.exc_info()[1]
      sys.exit('Cannot generate graph: ' + str(err))
    sys.exit(0)

  if not os.path.exists(img_file):
    sys.exit('File not found')


  image_loader = ip.imgloader.create(img_file, pixel_format, video_size)

  try:
    color_reader = ip.colorreader.create(
        output_format,
        image_loader,
        filter_type,
        out_json_file
    )
    color_reader.processing()
  except (AttributeError, ValueError) as err:
    err = sys.exc_info()[1]
    sys.exit('Cannot read image: ' + str(err))


if __name__ == '__main__':
  main()
