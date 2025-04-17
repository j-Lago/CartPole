import pygame
from dataclasses import dataclass
from pygame.constants import *

J_CROSS = 0
J_SQUARE = 2
J_TRIANGLE = 3
J_CIRCLE = 1
J_L1 = 9
J_L2 = 10
J_START = 6
J_SELECT = 4
J_PS = 5
J_PAD = 15
J_LEFT = 13
J_RIGHT = 14
J_UP = 11
J_DOWN = 12

@dataclass
class Bind:
    keydown: int | None = None
    keyup: int | None = None
    joybuttondown: int | None = None
    joybuttonup: int | None = None


def bind_test(event, bind):
    bind_match = False
    bind_match |= event.type == pygame.JOYBUTTONDOWN and event.button == bind.joybuttondown
    bind_match |= event.type == pygame.JOYBUTTONUP and event.button == bind.joybuttonup
    bind_match |= event.type == pygame.KEYDOWN and event.key == bind.keydown
    bind_match |= event.type == pygame.KEYUP and event.key == bind.keyup
    return bind_match





TOGGLE_PAUSE = Bind(keydown=K_SPACE, joybuttonup=J_START)
RESTART = Bind(keydown=K_ESCAPE, joybuttondown=J_PS)
