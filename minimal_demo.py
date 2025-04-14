from pygame import Vector2
from basescreen import BaseScreen
from canvas import Canvas

class MinimalDemo(BaseScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.canvases['main'] = Canvas(self.canvas_size, fonts=self.fonts, draw_fun=self.draw_main)
        self.mouse.set_visible(False)

    def draw_main(self, canvas: Canvas):
        pos = self.mouse_world_pos
        canvas.draw_text((255, 190, 30), self.fonts['huge'], f'{self.t:.1f}s', (0, 0))
        canvas.draw_circle((200, 200, 200), pos, .015)
        canvas.draw_text((200, 200, 200), self.fonts['small'], f'({pos[0]:.2f}, {pos[1]:.2f})', pos, anchor='midtop', shift=(0, -0.03))




if __name__ == '__main__':
    MinimalDemo()
