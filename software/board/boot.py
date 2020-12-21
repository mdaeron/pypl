from micropython import alloc_emergency_exception_buf
alloc_emergency_exception_buf(100)

import pyb
pyb.usb_mode('VCP')
