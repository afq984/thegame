import urllib.parse

import gym

from thegame.api import GameState, LockStepServer, RawClient
from thegame.thegame_pb2 import Controls


def _splitaddrport(addrport):
    assert '/' not in addrport
    r = urllib.parse.urlsplit(f'//{addrport}')
    return r.hostname, r.port


class SinglePlayerEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(
            self,
            *,
            server_bin='thegame',
            listen='localhost:50051',
            total_steps=16384,
            client_name='gym'
    ):
        """
        server_bin: relative or absolute path to thegame server.
                    defaults to finding `thegame` on $PATH
        listen: the [address]:port the server should be listening on
                omit the address to listen on all addresses
        """
        self.total_steps = total_steps
        hostname, port = _splitaddrport(listen)
        if hostname is None:
            hostname = 'localhost'
        self.server = LockStepServer(listen, bin=server_bin)
        self.client = RawClient(f'{hostname}:{port}', name=client_name)

    def __del__(self):
        try:
            s = self.server
        except AttributeError:
            pass
        else:
            s.terminate()

    def seed(self, seed):
        pass

    def step(self, action):
        controls = self.action_to_controls(action)
        self.client.send_controls(controls)
        self.server.wait_for_controls()
        self.server.tick()
        self.step_num += 1

        prev_state = self.game_state
        self.game_state = self.client.fetch_state()
        observation = self.game_state_to_observation(self.game_state)
        reward = self.get_reward(prev_state, self.game_state)
        return observation, reward, self.step_num >= self.total_steps, {}

    def reset(self):
        self.step_num = 0
        self.server.reset()
        self.server.tick()
        self.game_state = self.client.fetch_state()
        return self.game_state_to_observation(self.game_state)

    def action_to_controls(self, action) -> Controls:
        raise NotImplementedError

    def game_state_to_observation(self, game_state: GameState):
        raise NotImplementedError

    def get_reward(self, prev_state, current_state):
        raise NotImplementedError
