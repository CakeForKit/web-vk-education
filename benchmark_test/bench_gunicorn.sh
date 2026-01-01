#!/bin/bash

cd ../gunicorn
gunicorn -c ./config.py simple:dymanic_app > /dev/null
 
ab -n 100 -c 10 http://127.0.0.1:8081/?p1=1