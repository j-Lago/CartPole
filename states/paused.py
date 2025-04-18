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
        canvas.draw_text((255, 30, 30), self.game.fonts['huge'], f'PAUSED', (0, 0))
        canvas.draw_text((255, 30, 30), self.game.fonts['normal'], 'previous: ' + str(self.previous_state), (0, -.2))


