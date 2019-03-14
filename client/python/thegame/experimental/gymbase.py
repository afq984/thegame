import gym

from thegame.api import GameState
from thegame import thegame_pb2 as pb2


class BaseEnv(gym.Env):
    metadata = {'render.modes': ['human']}
    total_steps = 16384

    def __del__(self):
        self.server.terminate()

    def seed(self, seed):
        pass

    def step(self, action):
        controls = self.action_to_controls(action)
        self.client.send_controls(controls)

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

    def action_to_controls(self, action) -> pb2.Controls:
        raise NotImplementedError

    def game_state_to_observation(self, game_state: GameState):
        raise NotImplementedError

    def get_reward(self, prev_state, current_state):
        raise NotImplementedError
