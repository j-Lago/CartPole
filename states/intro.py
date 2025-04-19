import gamebase as gb
from bindings import *
import states as st
from game_draw import draw

class Intro(st.GameState):
    def __init__(self, game):
        super().__init__(game)
        self.intro_time = 2
        self.game.reset()
        self.timer_id = self.game.clock.start_timer(pygame.event.Event(END_OF_INTRO), period_seconds=self.intro_time)

    def __str__(self):
        return 'Intro'

    def enter(self):
        self.game.clock.resume_timer(self.timer_id)

    def exit(self):
        self.game.clock.pause_timer(self.timer_id)

    def handle_event(self, event: pygame.event):
        if bind_test(event, ABORT_INTRO):
            self.change_state(st.Running(self.game))
        if event.type == END_OF_INTRO:
            self.change_state(st.Running(self.game))

    def draw(self, canvas: gb.Canvas):
        draw(self, intro=True)
        canvas.draw_text((200, 200, 180), self.game.fonts['huge'], f'GET READY', (0, 0))
        canvas.draw_text((200, 200, 180), self.game.fonts['normal'], f'Game will start in {self.game.clock.get_timer_remaining(self.timer_id):.0f} s', (0, -.2))



