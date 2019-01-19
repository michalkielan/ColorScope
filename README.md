[![Travis CI](https://travis-ci.org/michalkielan/PixelClicker.svg?branch=master)](https://travis-ci.org/michalkielan/PixelClicker)

# ColorScope

[[https://github.com/michalkielan/ColorScope/blob/master/res/logo.png|alt=logo]]

Tool for debugging color issues.

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
$ ./color_reader.py -i image.jpeg -f format
```
