import gamebase as gb
import states as st
from bindings import *


class Running(st.GameState):
    def __init__(self, game):
        super().__init__(game)

    def __str__(self):
        return 'Running'

    def handle_event(self, event: pygame.event):
        if bind_test(event, TOGGLE_PAUSE):
            self.change_state(st.Paused(self.game))
        if event.type == TIMEOUT:
            self.change_state(st.Timeout(self.game))
        if bind_test(event, TEST):
            self.game.clock.start_timer(pygame.event.Event(TIMEOUT), period_seconds=9)

    def draw(self, canvas: gb.Canvas):
        remain = '(' + ', '.join(f"{self.game.clock.get_timer_remaining(id):.1f}" for id in self.game.clock.get_timers_ids()) + ')'
        canvas.draw_text((255, 30, 30), self.game.fonts['huge'], f'RUNNING', (0, .4))
        canvas.draw_text((255, 30, 30), self.game.fonts['normal'], f'{self.game.clock.t:.1f}s', (0, .2))
        canvas.draw_text((255, 190, 30), self.game.fonts['normal'], f'{remain}', (0, 0))

