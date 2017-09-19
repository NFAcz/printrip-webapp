### PrintRIP controller

## About
This small web application lets either projectionist or curator to control starting/stopping of PrintRip recording, as well as naming the resulting file.

## Requirements
    python >= 2.7
    Flask

## Usage
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

