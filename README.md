# ColorScope [![Travis CI](https://travis-ci.org/michalkielan/ColorScope.svg?branch=master)](https://travis-ci.org/michalkielan/ColorScope) [![Build status](https://ci.appveyor.com/api/projects/status/92q4lasei6qnrlkk/branch/master?svg=true)](https://ci.appveyor.com/project/michalkielan/colorscope/branch/master) [![Coverage Status](http://coveralls.io/repos/github/michalkielan/ColorScope/badge.svg?branch=master)](https://coveralls.io/github/michalkielan/ColorScope?branch=master)


![Logo](res/logo.png)

Tool for analyze the image quality

## Requirements
* python-opencv
* matplotlib
* scikit-image

```
$ sudo pip install opencv-python matplotlib scikit-image
```

## Usage
Output format supported: `rgb`, `yuv`, `hsv`, `hls`

```
$ ./colorscope.py -i image.jpeg -out_fmt=rgb
R      G      B
23     24     232
255    255    255
...
```

Raw input images
```
$ ./colorscope.py -i image.yuv -pix_fmt=nv21 -s 640x480 -out_fmt=rgb
```

Measure and plot data
```
$ ./colorscope.py -i reference.jpeg -out_fmt=hls -o ref.json
$ ./colorscope.py -i capture.jpeg -out_fmt=hls -o cap.json
$ ./colorscope.py -gen ref.json cap.json
```

#Quality metrics
Compare of two images quality using PSNR and SSIM metric for multichannel  
```
$ ./colorscope.py -cp metrics reference_image_dir ref_pixel_format ref_video_size capture_image_dir cap_pixel_format cap_video_size
```
For non raw images video size and pixel format can be ommited
```
$ ./colorscope.py -scp 0 ssim reference.jpg capture.jpg
$ ./colorscope.py -scp 0 psnr reference.jpg capture.jpg
```

Multichannel examples:
```
$ ./colorscope.py -cp ssim  reference.yuv nv12 1920x1080 capture.yuv nv12 1920x1080
$ ./colorscope.py -cp ssim reference.jpg capture.jpg
$ ./colorscope.py -cp psnr reference.jpg capture.jpg
```

Compare of two images quality using PSNR and SSIM metric for single channel
```
$ ./colorscope.py -scp metrics channel_number reference_image_dir ref__pxl_format ref_video_size capture_image_dir cap_pxl_format cap_video_size
```
Channel should be given accordingly to openCV color representation:
For BGR (typical way openCV stores RGB)
*blue 0
*green 1
*red 2

For YUV:
*Y 0
*U 1
*V 2

Single channel examples
```
$ ./colorscope.py -scp ssim 0  reference.yuv nv12 1920x1080 capture.yuv nv12 1920x1080
$ ./colorscope.py -scp psnr 2 reference.jpg capture.jpg
```
