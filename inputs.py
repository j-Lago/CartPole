
from typing import Callable
import pygame
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


class NoneInput():
    def __init__(self):
        self.value = 0.0

    def update(self, *args):
        return self.value


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

    def update(self, *args):
        if self.source is None:
            self.value = 0.0
        else:
            self.value = self.normalization(remove_dead_zone(self.source.get_axis(self.channel), self.dead_zone))
        return self.value


def remove_dead_zone(x, dead_zone):
    if abs(x) < dead_zone:
        return 0.0
    return x


class LinearController:
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
        init_r, pause_1, swing_l, pause_2 = 0.85, 1.1, 0.7, 1.2
        dir = 1
        if time < init_r:
            f = 1. * dir
        elif time < init_r + pause_1:
            f = 0. * dir
        elif time < init_r + pause_1 + swing_l:
            f = -1. * dir
        elif time < init_r + pause_1 + swing_l + pause_2:
            f = 0. * dir
        else:
            f = self.linear_controller(player, time)

        self.value = self.normalization(f)
        return self.value

    def linear_controller(self, player, time):
        dt = 1/player.fps
        x = player.model.y[0][0]
        v = player.model.y[1][0]

        # if time > 15:
        #     self.intx += dt * x
        #     self.th_target = math.pi + (+0.1*x +0.0*self.intx +0.000*v)
        # self.aux.update('')
        DTH_MAX = 30./180.*math.pi
        # dth = - self.aux.value * 5/180*math.pi
        dth = 0.
        kp = 0.0042 * 3
        ki = .0023/player.fps * 1
        kd = 0.006 * 6

        self.intx += dt * x
        dth_p = kp*x
        dth_i = ki*self.intx
        dth_d = kd*v
        dth = dth_p + dth_i + dth_d

        dth_sat = max(min(dth, DTH_MAX), -DTH_MAX)
        self.intx -= (dth-dth_sat)/ki  # anti windup
        self.th_target = math.pi + dth
        # print(dth)

        th = player.theta
        th = th + self.th_target if th < 0 else th - self.th_target
        a = player.omega
        f = -th * 1.8 - a * 1.7 + 0.1 * v

        return min(max(f, -1.), 1.)