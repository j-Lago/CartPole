import gamebase as gb
import states as st
from bindings import *


class Running(st.GameState):
    def __init__(self, game):
        super().__init__(game)
        self.game_time = 10
        self.timer_id = self.game.clock.start_timer(pygame.event.Event(TIMEOUT), period_seconds=self.game_time)

    def __str__(self):
        return 'Running'

    def enter(self):
        self.game.clock.resume_timer(self.timer_id)

    def exit(self):
        self.game.clock.pause_timer(self.timer_id)


    def handle_event(self, event: pygame.event):
        if bind_test(event, TOGGLE_PAUSE):
            self.change_state(st.Paused(self.game))
        if event.type == TIMEOUT:
            self.change_state(st.GameOver(self.game))
        if bind_test(event, RESTART):
            self.change_state(st.Intro(self.game))

    def draw(self, canvas: gb.Canvas):
        remain = '(' + ', '.join(f"{self.game.clock.get_timer_remaining(id):.1f}" for id in self.game.clock.get_timers_ids()) + ')'
        canvas.draw_text((255, 30, 30), self.game.fonts['huge'], f'RUNNING', (0, 0))
        canvas.draw_text((255, 30, 30), self.game.fonts['big'], f'Game will end in {self.game.clock.get_timer_remaining(self.timer_id):.0f} s', (0, -.4))


