
from typing import Callable
import pygame


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

    def update(self):
        self.value = self.normalization(remove_dead_zone(self.source.get_axis(self.channel), self.dead_zone))


def remove_dead_zone(x, dead_zone):
    if abs(x) < dead_zone:
        return 0.0
    return x