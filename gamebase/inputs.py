from abc import ABC, abstractmethod, abstractproperty
from typing import Callable, Self
import pygame
import math
import gamebase as gb

import os
os.environ['SDL_JOYSTICK_HIDAPI_PS4_RUMBLE'] = '1'


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


class BaseInput(ABC):
    def __init__(self, active_player_key):
        self.active_player_key = active_player_key

    @property
    @abstractmethod
    def value(self):
        pass

    @abstractmethod
    def update(self, player: Self) -> float:
        pass

    @abstractmethod
    def reset(self) -> None:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass



class NoneInput(BaseInput):
    def __init__(self, active_player_key: str | None = None):
        super().__init__(active_player_key)
    @property
    def value(self):
        return 0.0

    def update(self, *args):
        return 0.0

    def reset(self):
        pass

    @property
    def description(self) -> str:
        return 'None Input'


class Joystick(BaseInput):
    def __init__(self, source: pygame.joystick, channel:int=0, active_player_key:str|None=None, dead_zone: float = 0., initial_value = 0., normalization: Callable = lambda x: x):
        super().__init__(active_player_key)
        self.source = source
        self.channel = channel
        self.initial_value = initial_value
        self._value = initial_value
        self.dead_zone = dead_zone
        self.normalization = normalization

    @property
    def description(self) -> str:
        return 'Human: Joystick'

    @property
    def value(self):
        return self._value

    def reset(self):
        self._value = self.initial_value

    def update(self, *args):
        if self.source is None:
            self._value = 0.0
        else:
            self._value = self.normalization(remove_dead_zone(self.source.get_axis(self.channel), self.dead_zone))
        return self._value


def remove_dead_zone(x, dead_zone):
    if abs(x) < dead_zone:
        return 0.0
    return x


class LinearController(BaseInput):
    def __init__(self,
                 active_player_key: str | None = None,
                 initial_value=0.,
                 normalization: Callable = lambda x: x):
        super().__init__(active_player_key)
        self._value = initial_value
        self.initial_value = initial_value
        self.normalization = normalization

        self.th_target = math.pi

        self.kp = 0.0042 * 3
        self.ki = .0023/60 * 10
        self.kd = 0.006 * 6

        self.p_out = 0.0
        self.i_out = 0.0
        self.d_out = 0.0

        self.err_dev_filt_1 = 0.0
        self.int_err = 0.0
        self.err = 0.0
        self.err_1 = 0.0

    @property
    def value(self):
        return self._value

    @property
    def description(self):
        return 'Classic: Linear'

    def reset(self):
        self._value = self.initial_value
        self.th_target = math.pi

        self.int_err = 0.0
        self.err_dev_filt_1 = 0.0
        self.err = 0.0
        self.err_1 = 0.0

        self.p_out = 0.0
        self.i_out = 0.0
        self.d_out = 0.0
        self.d_out_1 = 0.0
        # self.aux = Joystick(source=pygame.joystick.Joystick(0), channel=2, dead_zone=0.05)

    def update(self, player):
        time = player.ticks / player.fps

        self.err_1 = self.err
        self.err = player.model.y[0][0]

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

        self._value = self.normalization(f)
        return self._value

    def linear_controller(self, player, time):
        dt = 1/player.fps
        # x = player.model.y[0][0]
        v = player.model.y[1][0]

        DTH_MAX = 35./180.*math.pi



        # p
        dth_p = self.kp * self.err

        # i
        self.int_err += dt * self.err
        dth_i = self.ki * self.int_err

        # d
        # dth_d = self.kd * v
        fc = 6


        tau = 1 / (2 * math.pi * fc)
        alpha = dt / (tau + dt)
        err_dev = (self.err - self.err_1) / dt
        err_dev_filt = alpha * err_dev + (1 - alpha) * self.err_dev_filt_1
        dth_d = self.kd * err_dev_filt

        dth = dth_p + dth_i + dth_d

        self.p_out = dth_p
        self.i_out = dth_i
        self.d_out = dth_d
        self.err_dev_filt_1 = err_dev_filt
        self.d_out_1 = self.d_out

        dth_sat = max(min(dth, DTH_MAX), -DTH_MAX)
        # if dth_sat != dth:
        #     print((dth - dth_sat) / self.ki)
        self.int_err -= (dth - dth_sat) / self.ki  # anti windup

        self.th_target = math.pi + dth_sat
        # print(dth)

        th = player.theta
        th = th + self.th_target if th < 0 else th - self.th_target
        a = player.omega
        f = -th * 1.8 - a * 1.7 + 0.1 * v

        return min(max(f, -1.), 1.)


class Keyboard(BaseInput):
    def __init__(self, source, key_left, key_right, active_player_key:str|None=None, key_intensity=None, initial_value = 0., normalization: Callable = lambda x: x):
        super().__init__(active_player_key)
        self.source = source
        self.key_left = key_left
        self.key_right = key_right
        self.key_intensity = key_intensity
        self.initial_value = initial_value
        self._value = initial_value
        self.normalization = normalization

    @property
    def description(self):
        return 'Human: Keyboard'

    @property
    def value(self):
        return self._value

    def reset(self):
        self._value = self.initial_value

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

        self._value = self.normalization(out)
        return self._value



class InputPool:
    def __init__(self):
        joystick = None
        for i in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()

        # self.input = Joystick(joystick, 2, normalization=lambda x: x)
        self.inputs: dict[str, gb.BaseInput] = dict()
        self.inputs['linear'] = gb.LinearController()
        if joystick is not None:
            self.inputs['joystick'] = gb.Joystick(joystick, channel=2, dead_zone=0.03)
        self.inputs['keyboard'] = gb.Keyboard(source=pygame.key, key_left=pygame.K_LEFT, key_right=pygame.K_RIGHT, key_intensity=pygame.K_RALT)
        self.inputs['none'] = gb.NoneInput()
        self.inputs['ia dummy'] = gb.NoneInput()
        self.inputs['joy2 dummy'] = gb.NoneInput()

    def __len__(self):
        return len(self.inputs)

    def get(self, owner_name: str, input_key:str=None):
        if input_key is None:
            for key in self.inputs.keys():
                if self.inputs[key].active_player_key is None:
                    self.inputs[key].active_player_key = owner_name
                    return self.inputs[key]
        return self.inputs[input_key]

    def values(self):
        return self.inputs.values()

    def keys(self):
        return self.inputs.keys()

    def items(self):
        return self.inputs.items()

    def __getitem__(self, item):
        return self.inputs[item]

    def __setitem__(self, key, value):
        self.inputs[key] = value



