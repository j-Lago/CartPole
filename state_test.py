import pygame.display

import gamebase as gb
from gamestate import GameState, Running, Paused


class MinimalDemo(gb.BaseScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.canvases['main'] = gb.Canvas(self.canvas_size, fonts=self.fonts, draw_fun=self.draw_main)
        self.mouse.set_visible(False)
        self.show_info()

        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print('joystick inicializado')


        self.event_loop_callback = self.process_event
        self.state = Running(self)

    def process_event(self, event: pygame.event):
        self.state.handle_event(event)


    def draw_main(self, canvas: gb.Canvas):

        pygame.display.set_caption(str(self.state))

        pos = self.mouse_world_pos
        canvas.draw_text((255, 190, 30), self.fonts['huge'], f'{self.t:.1f}s', (0, 0))
        canvas.draw_circle((200, 200, 200), pos, .015)
        canvas.draw_text((200, 200, 200), self.fonts['small'], f'({pos[0]:.2f}, {pos[1]:.2f})', pos, anchor='midtop', shift=(0, -0.03))


if __name__ == '__main__':
    MinimalDemo()