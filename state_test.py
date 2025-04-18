import pygame.display

import gamebase as gb
from gamestate import GameState, Running, Paused
from bindings import *


class MinimalDemo(gb.BaseScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.canvases['main'] = gb.Canvas(self.canvas_size, fonts=self.fonts, draw_fun=self.draw_main)
        self.show_info()

        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print('joystick inicializado')

        self.event_loop_callback = self.process_event
        self.state = Running(self)

        # pygame.time.set_timer(TIMEOUT, 2000, loops=1)
        # pygame.event.post(pygame.event.Event(TIMEOUT))



    def process_event(self, event: pygame.event):
        self.state.handle_event(event)

        # if bind_test(event, pygame.K_SPACE):
        #     pass


    def draw_main(self, canvas: gb.Canvas):

        pygame.display.set_caption(str(self.state))

        pos = self.mouse_world_pos


        # if self.t < 5:
        canvas.draw_text((255, 190, 30), self.fonts['small'], f'{self.clock.timers}', (0, 0))
        canvas.draw_text((255, 30, 30), self.fonts['huge'], f'{self.clock.t:.1f}s', (0, .4))
        # else:
        #     canvas.draw_text((255, 190, 30), self.fonts['huge'], f'TIMEOUT!', (0, 0))
        #     event = pygame.event.Event()


if __name__ == '__main__':
    MinimalDemo()