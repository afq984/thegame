import time

import grpc
import collections
from thegame import thegame_pb2, thegame_pb2_grpc


def gen():
    while True:
        time.sleep(2)
        print('send')
        yield thegame_pb2.Controls()


def main():
    channel = grpc.insecure_channel('localhost:50051')
    stub = thegame_pb2_grpc.TheGameStub(channel)
    for response in stub.Game(gen()):
        print('recv')
