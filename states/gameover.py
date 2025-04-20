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
        self.game.save_best_score()

    def handle_event(self, event: pygame.event):
        if bind_test(event, RESTART):
            self.change_state(st.Intro(self.game))

    def draw(self, canvas: gb.Canvas):
        if self.game.previous_state_screenshot is not None:
            self.game.previous_state_screenshot.set_alpha(127)
            canvas.blit(self.game.previous_state_screenshot, canvas.topleft)

        game_result = 'DRAW!'
        if self.game.players['p1'].score > self.game.players['p2'].score:
            game_result = 'P1 WINS!!'
        elif self.game.players['p1'].score < self.game.players['p2'].score:
            game_result = 'P2 WINS!'

        canvas.draw_text((200, 200, 180), self.game.fonts['huge'], f'GAME OVER', (0, 0))
        canvas.draw_text((200, 200, 180), self.game.fonts['big'], game_result, (0, -.3))
        canvas.draw_text((200, 200, 180), self.game.fonts['medium'], f'Press SPACE to resume', (0, -.5))

