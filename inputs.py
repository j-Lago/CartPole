import random
from typing import Callable
from functools import partial
import pygame
import torch
import numpy as np
from dqn import DQN, get_dims_from_weights
import math


JOYBUTTON: dict[str, int] = {
    'x': 0,
    'c': 1,
    's': 2,
    't': 3,
    'select': 4,
    'PS': 5,
    'start': 6,
    'L3': 7,
    'R3': 8,
    'L1': 9,
    'R1': 10,
    'up': 11,
    'down': 12,
    'left': 13,
    'right': 14,
    'pad': 15,
}


class Joystick():
    def __init__(self, source: pygame.joystick, channel, active_player_key:str|None=None, dead_zone: float = 0., initial_value = 0., normalization: Callable = lambda x: x):
        self.active_player_key = active_player_key
        self.source = source
        self.channel = channel
        self.initial_value = initial_value
        self.value = initial_value
        self.dead_zone = dead_zone
        self.normalization = normalization
        self.device_type = 'Human: Joystick'

    def reset(self):
        self.value = self.initial_value

    def update(self, player):
        self.value = self.normalization(remove_dead_zone(self.source.get_axis(self.channel), self.dead_zone))



class KeysControl():
    def __init__(self, source, key_left, key_right, active_player_key:str|None=None, key_intensity=None, initial_value = 0., normalization: Callable = lambda x: x):
        self.active_player_key = active_player_key
        self.source = source
        self.key_left = key_left
        self.key_right = key_right
        self.key_intensity = key_intensity
        self.initial_value = initial_value
        self.value = initial_value
        self.normalization = normalization
        self.device_type = 'Human: Keyboard'

    def reset(self):
        self.value = self.initial_value

    def update(self, player):
        keys = self.source.get_pressed()
        out = 0
        if keys[self.key_left]:
            out = -1
        if keys[self.key_right]:
            out = 1

        if self.key_intensity is not None:
            if keys[self.key_intensity]:
                out *= 0.5

        self.value = self.normalization(out)


class LinearControl:
    def __init__(self, active_player_key:str|None=None, initial_value=0., normalization: Callable = lambda x: x):
        self.active_player_key = active_player_key
        self.value = initial_value
        self.initial_value = initial_value
        self.normalization = normalization
        self.intx = 0.
        self.th_target = math.pi
        self.device_type = 'Classic: Linear'

    def reset(self):
        self.value = self.initial_value
        self.intx = 0.
        self.th_target = math.pi
        # self.aux = Joystick(source=pygame.joystick.Joystick(0), channel=2, dead_zone=0.05)

    def update(self, player):
        time = player.ticks / player.fps
        # coreografia inicial
        # init_r, pause_1, swing_l, pause_2 = 1.25, 1.25, 0.68, 1.5
        init_r, pause_1, swing_l, pause_2 = 1.49, 1.13, 0.59, 1.5
        if time < init_r:
            f = 1.
        elif time < init_r + pause_1:
            f = 0.
        elif time < init_r + pause_1 + swing_l:
            f = -1.
        elif time < init_r + pause_1 + swing_l + pause_2:
            f = 0.
        else:
            f = self.linear_controller(player, time)

        self.value = self.normalization(f)

    def linear_controller(self, player, time):
        dt = 1/player.fps
        x = player.model.y[0][0]
        v = player.model.y[1][0]

        # if time > 15:
        #     self.intx += dt * x
        #     self.th_target = math.pi + (+0.1*x +0.0*self.intx +0.000*v)
        # self.aux.update('')
        DTH_MAX = 30/180*math.pi
        # dth = - self.aux.value * 5/180*math.pi
        dth = 0.
        kp = 0.0042
        ki = .0023/player.fps
        kd = 0.006

        self.intx += dt * x
        dth_p = kp*x
        dth_i = ki*self.intx
        dth_d = kd*v
        dth = dth_p + dth_i + dth_d

        dth_sat = max(min(dth, DTH_MAX), -DTH_MAX)
        self.intx -= (dth-dth_sat)/ki  # anti windup
        self.th_target = math.pi + dth
        # print(dth)

        th = player.model.y[2][0]
        th = th + self.th_target if th < 0 else th - self.th_target
        a = player.model.y[3][0]
        f = -th * 1.5 - a * 1.7 + 0.1 * v

        return min(max(f, -1.), 1.)

class IAControl:
    def __init__(self, active_player_key:str|None=None, initial_value=0., weights_path='meta/play.pth', normalization: Callable = lambda x: x):
        self.active_player_key = active_player_key
        self.initial_value = initial_value
        self.value = initial_value
        self.normalization = normalization
        self.device_type = 'IA: Reinforcement Learning'

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        weights = torch.load(weights_path, weights_only=True)
        dims = get_dims_from_weights(weights)

        self.police_net = DQN(dims, self.device)
        self.police_net.load_state_dict(weights)

    def reset(self):
        self.value = self.initial_value


    def update(self, player):
        state = np.array([player.model.y[0][0], player.model.y[0][1],
                          player.model.y[1][0], player.model.y[1][1],
                          player.model.y[2][0], player.model.y[2][1],
                          player.model.y[3][0], player.model.y[3][1], player.fuel])
        pt_state = torch.Tensor(torch.tensor(np.array([state]), dtype=torch.float))
        with torch.no_grad():
            action = self.police_net(pt_state).argmax(dim=1).to(self.device)
        self.value = self.normalization((0., 1., -1., 0.5, -0.5)[action])

    # def update(self):
    #     self.value += self.normalization((random.random()*2-1)*0.6)
    #     self.value = max(-1., min(self.value, 1.))



def remove_dead_zone(x, dead_zone):
    if abs(x) < dead_zone:
        return 0.
    return x
