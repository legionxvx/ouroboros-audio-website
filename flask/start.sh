#!/bin/sh
#use LOCATION=local/remote depending on what your implementation is
#this affects the CSS imports, in our case, we needed it to be changed
#to url_for(/flask/) as root
rm flask-writer.pyc
export LOCATION=local
export FLASK_ENV=development
export FLASK_APP=flask-writer.py
python -m flask run
