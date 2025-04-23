import gamebase as gb
from enum import auto


class UserEvent(gb.UserEventEnum):
    INTRO_BEEP_TIMER = auto()
    END_OF_INTRO = auto()
    GAME_TIMEOUT = auto()

