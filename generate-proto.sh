# This scripts generates the required files for grpc
# Run this whenever the proto/*.proto gets updated
set -e
GOPATH="$PWD:$(go env GOPATH)" protoc -Iproto proto/thegame.proto --go_out=plugins=grpc:server/go/src/thegame/pb
cd client/python && python -m grpc_tools.protoc -I. thegame/thegame.proto --python_out=. --grpc_python_out=.
