### PrintRIP controller

## About
This web application allows either a projectionist, or a viewer to control live recording of a projected film from the cinema screen. DV camera required.

## Requirements
    python >= 2.7
    python-virtualenv
    dvgrab

## Usage
    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install -r requirements.exe
    $ python app.py -h
    usage: app.py [-h] [-c CONFIG] [-l LISTEN] [-p PORT] [-d]

    optional arguments:
      -h, --help            show this help message and exit
      -c CONFIG, --config CONFIG
                            Config file to use
      -l LISTEN, --listen LISTEN
                            Listen address
      -p PORT, --port PORT  Listen port
      -d, --debug           Flask debug

