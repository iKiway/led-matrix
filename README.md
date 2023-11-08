# led-matrix

## Setup
### 1. Allow Pip to install global packages
You first need to install the "pyhafas" libary via pip. It's importaint to say, that under the standard configuration of the Raspberry pi there is no download via pip without an virtual environment possible. Therefore some changes in the pip.config file are necessary (see [stack overflow](https://stackoverflow.com/questions/75608323/how-do-i-solve-error-externally-managed-environment-every-time-i-use-pip-3)):

Add following lines to ```~/.config/pip/pip.conf```

```
[global]
break-system-packages = true
```
This will allow pip to install packages globally. 
Please consider this option well.

### 2. Change Audio

### 3. Download the pip libarys
libary [pyhafas](https://github.com/FahrplanDatenGarten/pyhafas) required
```
pip install pyhafas
```
libary [Pillow](https://github.com/python-pillow/Pillow/) required
```
pip install pillow
```
### 4. Download
download the libary [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix/blob/master/bindings/python/README.md) 
## Usage
This libary is for matrices with the sice 64x32 pixel (non Adafruit).
