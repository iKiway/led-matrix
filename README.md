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
Download the libary [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix/tree/master).
This libary can't be downloaded with pip. 

Therefore use:
```
sudo apt-get update
sudo apt-get install git
git clone https://github.com/hzeller/rpi-rgb-led-matrix
```
after that you have to activate the libary:
```
cd rpi-rgb-led-matrix
sudo apt-get update
sudo apt-get install python3-dev python3-pillow -y
make-build-python PYTHON=$(which python3)
sudo make install-python PYTHON=$(which python3)
```
## Usage
This libary is for matrices with the sice 64x32 pixel (non Adafruit).

The program can only be started as sudo!

