#!/bin/sh
#use LOCATION=local if you're running locally
rm flask-writer.pyc
export LOCATION=local
export FLASK_ENV=development
export FLASK_APP=flask-writer.py
python -m flask run
