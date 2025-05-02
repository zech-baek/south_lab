# ! /usr/bin/env python
# coding=utf-8

import os
import sys
import pathlib

try:
    # try to use __file__
    misc_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # fallback to sys.argv[0] or current working directory
    if len(sys.argv) > 0:
        misc_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    else:
        misc_dir = os.getcwd()

log_dir = pathlib.Path(misc_dir).parent/"log"

if not log_dir.exists():
    log_dir.mkdir(parents=True, exist_ok=True)


from PIL import Image
import pillow_heif
import os, sys

for file in os.listdir(log_dir):
    raw = pillow_heif.read_heif(file)
    converted_image = Image.frombytes(raw.mode, raw.size, raw.data, "raw")
    root, old_extension = os.path.splitext(file)
    new_filename = root + '.' + "jpg"
    converted_image.save(new_filename)