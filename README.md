# ColorScope [![Travis CI](https://travis-ci.org/michalkielan/ColorScope.svg?branch=master)](https://travis-ci.org/michalkielan/ColorScope) [![Build status](https://ci.appveyor.com/api/projects/status/92q4lasei6qnrlkk/branch/master?svg=true)](https://ci.appveyor.com/project/michalkielan/colorscope/branch/master) [![Coverage Status](http://coveralls.io/repos/github/michalkielan/ColorScope/badge.svg?branch=master&service=github)](https://coveralls.io/github/michalkielan/ColorScope?branch=master)


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
