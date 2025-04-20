from binding_test import *


TOGGLE_PAUSE = Bind(keydown=K_SPACE, joybuttonup=J_START)
RESTART = Bind(keydown=K_ESCAPE, joybuttonup=J_PS)
ABORT_INTRO = Bind(keydown=K_RETURN, joybuttonup=J_CROSS)
ABORT_NEW_SETTINGS = Bind(keydown=K_ESCAPE, joybuttonup=J_CIRCLE)
CONFIRM_NEW_SETTINGS = Bind(keydown=K_RETURN, joybuttonup=J_CROSS)
SETTINGS = Bind(keydown=K_F2, joybuttonup=J_SELECT)