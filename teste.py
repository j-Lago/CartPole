import pygame.mouse

import gamebase as gb
from pygame import Vector2


class Teste(gb.BaseScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.canvas.draw_fun = self.draw_main
        # self.mouse.set_visible(False)
        self.show_info()
        self.frame = gb.Frame(self.canvas, (0, 0, .7, .6), alpha=200, origin='topleft')
        self.slider1 = gb.Slider(self.frame, (0, 0.0, 0.1, 0.6), max_value=0.5, min_value=-0.5)

        self.slider = gb.Slider(self.canvas, (-.4, 0.8, 0.1, 0.6), max_value=0.5, min_value=-0.5)
        self.th = 0.0

        # self.canvas.bias = (500, 500)

    def draw_main(self, canvas: gb.Canvas):
        canvas.fill(self.cols['bg'])

        canvas.draw_circle((90, 240, 180), self.mouse.pos, .12, 2)

        # pos = draw_grid(self, canvas)
        pos = self.mouse.pos

        points = gb.Points((0, 0), (0.6, 0.1), (0.4, 0.6))



        rect = gb.Rect_f(-0.9, -0.5, .5, .2)
        color, width = ((255, 255, 0), 3) if rect.point_collision(pos) else ((127, 127, 255), 2)
        canvas.draw_rect(color, rect, width)

        center = Vector2(.6, -.6)
        r = .2
        # color, width = ((255, 255, 0), 3) if gb.point_circle_collision(pos, center, r) else ((127, 127, 255), 2)
        # canvas.draw_circle(color, center, r, width)

        self.slider1.update(self)
        self.frame.update(self)
        # self.slider.update(self)

        self.th -= .1 * self.slider.value
        canvas.draw_polygon((255, 255, 255), points.rotate(self.th, (0.4, 0.2)))
        # canvas.draw_circle((200, 200, 200), pos, .015)
        # canvas.draw_text((200, 200, 200), self.fonts['small'], f'({pos[0]:.2f}, {pos[1]:.2f})', pos, anchor='midtop',
        #                  shift=(0, -0.03))

        canvas.draw_circle((240, 180, 90), self.mouse.pos, .1, 2)




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

    mouse_pos = game.mouse.pos
    if snap_to_grid:
        mouse_pos = round((mouse_pos[0]-center[0]) / dx) * dx + center[0], round((mouse_pos[1]-center[1]) / dy) * dy + center[1]

    canvas.draw_line(origin_color, (center[0], ymin), (center[0], ymax))
    canvas.draw_line(origin_color, (xmin, center[1]), (xmax, center[1]))

    return mouse_pos





if __name__ == '__main__':
    Teste()


