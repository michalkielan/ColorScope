[![Travis CI](https://travis-ci.org/michalkielan/PixelClicker.svg?branch=master)](https://travis-ci.org/michalkielan/PixelClicker)

# PixelClicker

Tool for debugging color issues. Print the RGB value of each clicked pixel

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
$ ./pixel_clicker.py -i image.jpeg -f format
```
