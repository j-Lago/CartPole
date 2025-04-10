import pygame.font
from basescreen import BaseScreen
from canvas import Canvas


class MinimalDemo(BaseScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.canvases['main'] = Canvas(self.canvas_size, fonts=self.fonts, draw_fun=self.draw_main)

    def draw_main(self, canvas: Canvas):
        canvas.draw_text((230, 180, 30), self.fonts['huge'], f'{self.t:.1f}s', (0, 0))


if __name__ == '__main__':
    MinimalDemo()
