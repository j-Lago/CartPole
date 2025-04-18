import pygame.display
import gamebase as gb
from states import Intro
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
        self.state = Intro(self)

    def process_event(self, event: pygame.event):
        self.state.handle_event(event)

    def draw_main(self, canvas: gb.Canvas):

        pygame.display.set_caption(str(self.state))
        self.state.update()
        self.state.draw(canvas)




if __name__ == '__main__':
    MinimalDemo()