import gamebase as gb
from bindings import *
import states as st


class GameOver(st.GameState):
    def __init__(self, game):
        super().__init__(game)

    def __str__(self):
        return 'GameOver'

    def enter(self):
        self.game.clock.cancel_timers()

    def handle_event(self, event: pygame.event):
        if bind_test(event, RESTART):
            self.change_state(st.Intro(self.game))

    def draw(self, canvas: gb.Canvas):
        canvas.draw_text((255, 30, 30), self.game.fonts['huge'], f'GAME OVER', (0, 0))
        canvas.draw_text((255, 30, 30), self.game.fonts['big'], f'Press ESC to restart', (0, -.4))


