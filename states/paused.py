import gamebase as gb
import states as st
from bindings import *


class Paused(st.GameState):
    def __init__(self, game):
        super().__init__(game)
        self.previous_state = None

    def __str__(self):
        return 'Paused'

    def handle_event(self, event: pygame.event):
        if bind_test(event, TOGGLE_PAUSE):
            self.change_state(self.previous_state)
        if bind_test(event, RESTART):
            self.change_state(st.Intro(self.game))

    def draw(self, canvas: gb.Canvas):
        if self.game.previous_state_screenshot is not None:
            self.game.previous_state_screenshot.set_alpha(127)
            canvas.blit(self.game.previous_state_screenshot, canvas.topleft)
        canvas.draw_text((255, 30, 30), self.game.fonts['huge'], f'PAUSED', (0, .5))
        canvas.draw_text((255, 30, 30), self.game.fonts['normal'], 'previous: ' + str(self.previous_state), (0, .3))


