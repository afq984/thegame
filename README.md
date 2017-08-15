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
pip3 install --upgrade git+https://github.com/afg984/thegame.git#subdirectory=client/python
```

### Interactive Client

```
python3 -m thegame.gui
```

### Writing your own client

Use `client/python/example.py` as a template to start with

To start the client: `python example.py`

## Server

1. go to `server/go`
2. `make run`
