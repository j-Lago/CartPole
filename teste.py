import pygame.mouse

import gamebase as gb
from pygame import Vector2


class Teste(gb.BaseScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.canvas.draw_fun = self.draw_main
        # self.mouse.set_visible(False)
        self.show_info()
        self.frame = gb.Frame(self.canvas, (0.4, -0.2, .35, .7), alpha=200, origin='topleft')
        self.slider = gb.Slider(self.frame, (0.05, -0.05, 0.1, 0.6), text='w', font=self.fonts['small'], max_value=0.5, min_value=-0.5)
        self.slider2 = gb.Slider(self.frame, (0.2, -0.05, 0.1, 0.6), text='s', font=self.fonts['small'], max_value=1.8, min_value=0.2, init_value=1.0)

        self.frame_rgb = gb.Frame(self.canvas, (0.8, -0.2, .5, .6), alpha=200, origin='topleft')
        self.slider_r = gb.Slider(self.frame_rgb, (0.05, -0.05, 0.10, 0.5), text='r', font=self.fonts['small'], min_value=0, max_value=255, init_value=127, fg_color=(255,90,90))
        self.slider_g = gb.Slider(self.frame_rgb, (0.2, -0.05, 0.10, 0.5), text='g', font=self.fonts['small'], min_value=0, max_value=255, init_value=127, fg_color=(90,255,90))
        self.slider_b = gb.Slider(self.frame_rgb, (0.35, -0.05, 0.10, 0.5), text='b', font=self.fonts['small'], min_value=0, max_value=255, init_value=127, fg_color=(90,90,255))

        self.th = 0.0

        # self.canvas.bias = (500, 500)

    def draw_main(self, canvas: gb.Canvas):
        canvas.fill(self.cols['bg'])



        points = gb.Points((0, 0), (0.6, 0.1), (0.4, 0.6))


        self.th -= .1 * self.slider.value
        color = int(self.slider_r.value), int(self.slider_g.value), int(self.slider_b.value)
        canvas.draw_polygon(color, points.rotate(self.th, (0.4, 0.2)).scale(self.slider2.value))

        self.frame.update(self)
        self.frame_rgb.update(self)





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


