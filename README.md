# led-matrix

## setup
### 1. Allow Pip to install global packages
You first need to install the "pyhafas" libary via pip. It's importaint to say, that under the standard configuration of the Raspberry pi there is no download via pip without an virtual environment possible. Therefore some changes in the pip.config file are necessary (see [stack overflow](https://stackoverflow.com/questions/75608323/how-do-i-solve-error-externally-managed-environment-every-time-i-use-pip-3)):

Add following lines to ```~/.config/pip/pip.conf```

```
[global]
break-system-packages = true
```
This will allow pip to install packages globally. 
Please consider this option well.

### 2. Download the pip libarys
Only libary [pyhafas](https://github.com/FahrplanDatenGarten/pyhafas) required
```
pip install pyhafas
```
