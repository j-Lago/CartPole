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

        angle = 0
        pos = self.game.mouse_world_pos

        canvas.draw_polygon((90, 90, 100),
                            gb.translate_vec2s(gb.rotate_vec2s(((0.06, 0.05), (0.08, -0.1), (-0.08, -0.1), (-0.06, 0.05)), angle), pos))  # angle
        canvas.draw_polygon((120, 120, 130),
                            gb.translate_vec2s(((0.1, 0.0), (0.1, 0.6), (0.06, 0.75), (0.0, 0.8), (-0.06, 0.75), (-0.1, 0.6), (-0.1, 0.0)), pos))

        canvas.draw_circle((255, 200, 60), pos+(0, 0.25), 0.05, width=0, draw_top_left=True, draw_bottom_right=True)
        canvas.draw_circle((0, 0, 0), pos+(0, 0.25), 0.05, width=0, draw_top_right=True, draw_bottom_left=True)

