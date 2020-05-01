#!/bin/bash

source config.sh
FLASK_APP=app.py FLASK_DEBUG=1 python3 -m flask run --host=$IP --port=$PORT