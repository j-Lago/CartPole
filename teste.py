import pygame.mouse

import gamebase as gb
from pygame import Vector2


class Teste(gb.BaseScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.canvas.draw_fun = self.draw_main
        # self.mouse.set_visible(False)
        self.show_info()

        self.scope = gb.Scope(self.canvas, name='frame time', legend=('active', 'total'), fps=self.clock.fps,
                              alpha=200, color=self.cols['info'],
                              x_scale=0.5,
                              pos=(-1.6, -0.65),
                              size=(320, 180), maxlen=400, visible=True)

        self.frame = gb.Frame(self.canvas, (0.4, -0.2, .35, .75), alpha=200, origin='topleft')
        self.slider = gb.Slider(self.frame, (0.05, -0.05, 0.1, 0.65), text='w', font=self.fonts['small'], max_value=0.5, min_value=-0.5)
        self.slider2 = gb.Slider(self.frame, (0.2, -0.05, 0.1, 0.65), text='s', font=self.fonts['small'], max_value=1.8, min_value=0.2, init_value=1.0)

        self.frame_rgb = gb.Frame(self.canvas, (0.8, -0.2, .5, .75), alpha=200, origin='topleft')
        self.slider_r = gb.Slider(self.frame_rgb, (0.05, -0.05, 0.10, 0.5), text='r', font=self.fonts['small'], min_value=0, max_value=255, init_value=127, fg_color=(255,90,90))
        self.slider_g = gb.Slider(self.frame_rgb, (0.2, -0.05, 0.10, 0.5), text='g', font=self.fonts['small'], min_value=0, max_value=255, init_value=127, fg_color=(90,255,90))
        self.slider_b = gb.Slider(self.frame_rgb, (0.35, -0.05, 0.10, 0.5), text='b', font=self.fonts['small'], min_value=0, max_value=255, init_value=127, fg_color=(90,90,255))

        self.button = gb.Button(self.frame_rgb, (0.1, -0.6, .3, .1), text='reset', font=self.fonts['small'], release_callback=self.color_reset)

        self.frame_bt = gb.Frame(self.canvas, (-.5, -0.2, .2, .56), alpha=200, origin='topleft')
        self.button_a = gb.Button(self.frame_bt, (0.05, -0.05, .1, .1), text='A', font=self.fonts['small'], toggle=True)
        self.button_b = gb.Button(self.frame_bt, (0.05, -0.17, .1, .1), text='B', font=self.fonts['small'], toggle=True)
        self.button_c = gb.Button(self.frame_bt, (0.05, -0.29, .1, .1), text='C', font=self.fonts['small'], toggle=True)
        self.button_d = gb.Button(self.frame_bt, (0.05, -0.41, .1, .1), text='D', font=self.fonts['small'], toggle=True)

        self.frame_bt2 = gb.Frame(self.canvas, (-.2, -0.2, .2, .56), alpha=200, origin='topleft')
        self.button_e = gb.Button(self.frame_bt2, (0.05, -0.05, .1, .1), text='E', font=self.fonts['small'], radio=True)
        self.button_f = gb.Button(self.frame_bt2, (0.05, -0.17, .1, .1), text='F', font=self.fonts['small'], radio=True, toggle_callback=self.toggle_callback)
        self.button_g = gb.Button(self.frame_bt2, (0.05, -0.29, .1, .1), text='G', font=self.fonts['small'], radio=True)
        self.button_h = gb.Button(self.frame_bt2, (0.05, -0.41, .1, .1), text='H', font=self.fonts['small'], toggle=True, on_color=(30,180,180))


        self.th = 0.0

    def toggle_callback(self, button):
        print(f'button F: {button.state}')

    def color_reset(self, button):
        for slider in (self.slider_r, self.slider_g, self.slider_b):
            slider.reset()

    def draw_main(self, canvas: gb.Canvas):
        canvas.fill(self.cols['bg'])



        points = gb.Points((0, 0), (0.6, 0.1), (0.4, 0.6))


        self.th -= .1 * self.slider.value
        color = int(self.slider_r.value), int(self.slider_g.value), int(self.slider_b.value)
        canvas.draw_polygon(color, points.rotate(self.th, (0.4, 0.2)).scale(self.slider2.value))

        self.frame.update(self)
        self.frame_rgb.update(self)
        self.frame_bt.update(self)
        self.frame_bt2.update(self)

        # scope
        x = self.clock.t
        total_frame_time = 1 / self.real_fps if self.real_fps != 0 else 0
        y = (self.last_active_frame_time * self.clock.fps - 1, total_frame_time * self.clock.fps - 1)
        self.scope.append(x, y)
        self.scope.update(self)






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


