#!/usr/bin/env python3.5
"""Script to read the color values"""

import argparse
import sys
import os
import ip.imgloader
import ip.colorreader


def parse_video_size_arg(video_size):
  if video_size != '':
    w, h = video_size.split('x', 1)
    return int(w), int(h)
  return None

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

  args = parser.parse_args()
  pixel_format = args.pixel_format.lower()
  output_format = args.output_format.lower()
  video_size = parse_video_size_arg(args.video_size)
  filter_type = args.filter.lower()
  img_file = args.imgfile

  if not os.path.exists(img_file):
    sys.exit('File not found')

  image_loader = ip.imgloader.create(img_file, pixel_format, video_size)

  try:
    color_reader = ip.colorreader.create(output_format, image_loader, filter_type)
    color_reader.processing()
  except (AttributeError, ValueError) as err:
    err = sys.exc_info()[1]
    sys.exit('Cannot read image: ' + str(err))


if __name__ == '__main__':
  main()
