import gamebase as gb
from bindings import *
import states as st


class Timeout(st.GameState):
    def __init__(self, game):
        super().__init__(game)

    def __str__(self):
        return 'Timeout'

    def enter(self):
        self.game.clock.cancel_timers()

    def handle_event(self, event: pygame.event):
        if bind_test(event, RESTART):
            self.change_state(st.Intro(self.game))

    def draw(self, canvas: gb.Canvas):
        if self.game.previous_state_screenshot is not None:
            self.game.previous_state_screenshot.set_alpha(127)
            canvas.blit(self.game.previous_state_screenshot, canvas.topleft)
        canvas.draw_text((200, 200, 180), self.game.fonts['huge'], f'TIMEOUT', (0, 0))
        canvas.draw_text((200, 200, 180), self.game.fonts['medium'], f'Press ESC to restart', (0, -.2))


