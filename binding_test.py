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


def bind_test(event: pygame.event.Event, bind: Bind):
    if bind.joybuttondown is not None:
        if event.type == pygame.JOYBUTTONDOWN and event.button == bind.joybuttondown:
            return True
    if bind.joybuttonup is not None:
        if event.type == pygame.JOYBUTTONUP and event.button == bind.joybuttonup:
            return True
    if bind.keydown is not None:
        if event.type == pygame.KEYDOWN and event.key == bind.keydown:
            return True
    if bind.keyup is not None:
        if event.type == pygame.KEYUP and event.key == bind.keyup:
            return True
    return False


