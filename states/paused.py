import gamebase as gb
import states as st
from bindings import *


class Paused(st.GameState):
    def __init__(self, game):
        super().__init__(game)
        self.previous_state = None

    def __str__(self):
        return 'Paused'

    def enter(self):
        self.game.clock.pause()

    def exit(self):
        self.game.clock.resume()

    def handle_event(self, event: pygame.event):
        if bind_test(event, TOGGLE_PAUSE):
            self.change_state(self.previous_state)
        if bind_test(event, RESTART):
            self.change_state(st.Intro(self.game))

    def draw(self, canvas: gb.Canvas):
        if self.game.previous_state_screenshot is not None:
            self.game.previous_state_screenshot.set_alpha(127)
            canvas.blit(self.game.previous_state_screenshot, canvas.topleft)
        canvas.draw_text((200, 200, 180), self.game.fonts['huge'], f'PAUSED', (0, 0))
        canvas.draw_text((200, 200, 180), self.game.fonts['medium'], f'Press SPACE to resume', (0, -.2))
