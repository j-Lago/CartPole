import pygame.mouse

import gamebase as gb
from pygame import Vector2


class Teste(gb.BaseScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.canvases['main'] = gb.Canvas(self.canvas_size, fonts=self.fonts, draw_fun=self.draw_main)
        self.mouse.set_visible(False)
        # self.show_info()

    def draw_main(self, canvas: gb.Canvas):
        # pos = self.mouse_world_pos
        pos = draw_grid(self, canvas)


        points = gb.Points((0, 0), (0.4, 0.2), (0.4, 0.6))

        canvas.draw_polygon((255, 255, 255), points, 2)

        canvas.draw_circle((200, 200, 200), pos, .015)
        canvas.draw_text((200, 200, 200), self.fonts['small'], f'({pos[0]:.2f}, {pos[1]:.2f})', pos, anchor='midtop',
                         shift=(0, -0.03))




def draw_grid(game: Teste, canvas: gb.Canvas, dx=.05, dy=.05, snap_to_grid=True):
    xmin, xmax, ymin, ymax = canvas.xmin, canvas.xmax, canvas.ymin, canvas.ymax
    w, h = xmax-xmin, ymax-ymin
    center = Vector2(w/2+xmin, h/2+ymin)
    color = (127, 127, 127)
    origin_color = (255, 255, 255)

    for i in range(1, int(w/dx/2)+1):
        canvas.draw_line(color, (x := center[0] + dx * i, ymin), (x, ymax))
        canvas.draw_line(color, (x := center[0] - dx * i, ymin), (x, ymax))

    for i in range(1, int(h/dy/2)+1):
        canvas.draw_line(color, (xmin, y := center[1] + dy * i), (xmax, y))
        canvas.draw_line(color, (xmin, y := center[1] - dy * i), (xmax, y))

    canvas.draw_line(origin_color, (center[0], ymin), (center[0], ymax))
    canvas.draw_line(origin_color, (xmin, center[1]), (xmax, center[1]))

    mouse_pos = game.mouse_world_pos
    if snap_to_grid:
        mouse_pos = round((mouse_pos[0]-center[0]) / dx) * dx + center[0], round((mouse_pos[1]-center[1]) / dy) * dy + center[1]
        # game.mouse_world_pos = snapped_pos

    return mouse_pos





if __name__ == '__main__':
    Teste()


