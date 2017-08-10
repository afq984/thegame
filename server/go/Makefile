.PHONY: default
default: environment
	GOPATH=$(PWD)/vendor:$(PWD) go build thegame

.PHONY: environment
environment:
	GOPATH=$(PWD)/vendor:$(PWD) go get google.golang.org/grpc
