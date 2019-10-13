###### 2017/2018 清大資工新生營 - Python 程式設計
# thegame
[![CircleCI](https://circleci.com/gh/afg984/thegame.svg?style=svg)](https://circleci.com/gh/afg984/thegame)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Client

### Installation

First, make sure you have python (3.6 or later required)

Then install with pip:

```
python3 -m pip install --upgrade git+https://github.com/afg984/thegame.git#subdirectory=client/python
```

You may want to use the `--user` flag.

For windows, replace `python3` with `py` or whatever refers to the correct python.

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

The API documentation is at: https://afq984.github.io/thegame/

## Server

1. Install go https://golang.org/

2. Install the server

   ```
   go get github.com/afg984/thegame/server/go/thegame
   ```

3. Run the server

   ```
   $GOPATH/bin/thegame [-listen [host]:port] [-tps N]
   ```
