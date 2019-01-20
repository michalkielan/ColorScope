# ColorScope [![Travis CI](https://travis-ci.org/michalkielan/ColorScope.svg?branch=master)](https://travis-ci.org/michalkielan/ColorScope) [![Coverage Status](https://coveralls.io/repos/github/michalkielan/ColorScope/badge.svg?branch=master)](https://coveralls.io/github/michalkielan/ColorScope?branch=master)

![Logo](res/logo.png)

Tool for analyze the image quality

## Requirements 
```
python-opencv
```

### Linux

#### Debian/Ubuntu
```
$ sudo apt-get install python-opencv
$ sudo pip install opencv-python
```

## Usage
Format supported: RGB, YUV

```
$ ./colorscope.py -i image.jpeg -f=RGB
```
