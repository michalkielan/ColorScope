[![Travis CI](https://travis-ci.org/michalkielan/PixelClicker.svg?branch=master)](https://travis-ci.org/michalkielan/PixelClicker)

# ColorScope

![Logot](res/logo.png)

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
