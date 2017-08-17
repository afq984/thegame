###### 2017 清大資工新生營 - Python 程式設計
# thegame
[![Maintenance](https://img.shields.io/maintenance/yes/2017.svg)]()
[![Python](https://img.shields.io/badge/Python-3.6-brightgreen.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Client

### Installation

First, make sure you have python (3.6 or later required) and Qt5

Then install with pip:

```
python3 -m pip install --upgrade git+https://github.com/afg984/thegame.git#subdirectory=client/python
```

You may want to use the `--user` flag

### Interactive Client

```
python3 -m thegame.gui [SERVER_ADDRESS]
```

Where `[SERVER_ADDRESS]` is the `host:port` of the server, which defaults to `localhost:50051`

### Writing your own client

Use `client/python/example.py` as a template to start with

To start the client:

```
python3 example.py [SERVER_ADDRESS]
```

The API documentation is at: https://afg984.github.io/thegame/

## Server

1. go to `server/go`
2. `make run`
