import math
import random

import pygame.mouse

import gamebase as gb
from pygame import Vector2


class Teste(gb.BaseScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.canvas.draw_fun = self.draw_main
        # self.mouse.set_visible(False)
        # self.show_info()

        self.scope = gb.Scope(self.canvas, name='frame time', legend=('active', 'total'), fps=self.clock.fps,
                              alpha=200, color=self.cols['info'],
                              x_scale=0.5,
                              pos=(-1.6, -0.65),
                              size=(320, 180), maxlen=400, visible=True)

        self.frame = gb.Frame(self.canvas, (0.4, -0.2, .5, .75), alpha=200, origin='topleft')
        self.slider = gb.Slider(self.frame, (0.05, -0.05, 0.1, 0.65), text='w', font=self.fonts['small'], max_value=0.5, min_value=-0.5)
        self.slider2 = gb.Slider(self.frame, (0.2, -0.05, 0.1, 0.65), text='s', font=self.fonts['small'], max_value=1.8, min_value=0.2, init_value=1.0)
        self.slider3 = gb.Slider(self.frame, (0.35, -0.05, 0.1, 0.65), text='a', font=self.fonts['small'], max_value=math.pi, min_value=-math.pi, init_value=-1.8)

        self.frame_rgb = gb.Frame(self.canvas, (0.95, -0.2, .5, .75), alpha=200, origin='topleft')
        self.slider_r = gb.Slider(self.frame_rgb, (0.05, -0.05, 0.10, 0.5), text='r', font=self.fonts['small'], min_value=0, max_value=255, init_value=120, fg_color=(255,90,90))
        self.slider_g = gb.Slider(self.frame_rgb, (0.2, -0.05, 0.10, 0.5), text='g', font=self.fonts['small'], min_value=0, max_value=255, init_value=190, fg_color=(90,255,90))
        self.slider_b = gb.Slider(self.frame_rgb, (0.35, -0.05, 0.10, 0.5), text='b', font=self.fonts['small'], min_value=0, max_value=255, init_value=50, fg_color=(90,90,255))
        self.button = gb.Button(self.frame_rgb, (0.1, -0.6, .3, .1), text='reset', text_font=self.fonts['small'], release_callback=self.color_reset)

        self.frame_bt = gb.Frame(self.canvas, (-.45, -0.2, .2, .56), alpha=200, origin='topleft')
        self.button_a = gb.Button(self.frame_bt, (0.05, -0.05, .1, .1), text='A', text_font=self.fonts['small'], toggle=True)
        self.button_b = gb.Button(self.frame_bt, (0.05, -0.17, .1, .1), text='B', text_font=self.fonts['small'], toggle=True)
        self.button_c = gb.Button(self.frame_bt, (0.05, -0.29, .1, .1), text='C', text_font=self.fonts['small'], toggle=True)
        self.button_d = gb.Button(self.frame_bt, (0.05, -0.41, .1, .1), text='D', text_font=self.fonts['small'], toggle=True)

        self.frame_bt2 = gb.Frame(self.canvas, (-.2, -0.2, .43, .56), alpha=200, origin='topleft')
        self.button_e = gb.Button(self.frame_bt2, (0.05, -0.05, .1, .1), text=('■', '●'), text_font=self.fonts['small'], radio=True, label='button E')
        self.button_f = gb.Button(self.frame_bt2, (0.05, -0.17, .1, .1), text=('■', '●'), text_font=self.fonts['small'], radio=True, label='button B')
        self.button_g = gb.Button(self.frame_bt2, (0.05, -0.29, .1, .1), text=('■', '●'), text_font=self.fonts['small'], radio=True, label='button G')
        self.button_h = gb.Button(self.frame_bt2, (0.05, -0.41, .1, .1), text=('■', '●'), text_font=self.fonts['small'], radio=True, label='button H')

        self.frame_bt3 = gb.Frame(self.canvas, (-0.95, -0.2, .45, .56), alpha=200, origin='topleft')
        self.button_i = gb.Button(self.frame_bt3, (0.05, -0.05, .35, .1), text='normal', text_font=self.fonts['small'], press_callback=lambda b: print(f'click'))
        self.button_j = gb.Button(self.frame_bt3, (0.05, -0.17, .35, .1), text='toggle', text_font=self.fonts['small'], toggle=True, toggle_callback=lambda b: print(f'toggled: {b.state}'))
        self.button_k = gb.Button(self.frame_bt3, (0.05, -0.29, .35, .1), text='inactive', text_font=self.fonts['small'], active=False, press_callback=lambda b: print('should not be clicked'))
        self.button_l = gb.Button(self.frame_bt3, (0.05, -0.41, .35, .1), text='unselectable', text_font=self.fonts['small'], unselectable=True, press_callback=lambda b: print('should not be clicked'))

        self.frame_bt4 = gb.Frame(self.canvas, (-0.65, 0.6, .45, .33), alpha=200, origin='topleft')
        self.spawn_n = gb.Button(self.frame_bt4, (0.05, -0.05, .35, .1), text='spawn N', text_font=self.fonts['small'], press_callback=self.spawn_normal_particle)
        self.spawn_c = gb.Button(self.frame_bt4, (0.05, -0.17, .35, .1), text='spawn C', text_font=self.fonts['small'], press_callback=self.spawn_collidable_particle)

        self.particle = None
        self.th = 0.0
        self.dth = 0.0
        self.th0 = 0.0

        self.canon_origin = Vector2(-0.1, .9)

    @property
    def canon_dir(self):
        return Vector2(self.slider2.value, 0.0).rotate_rad(self.slider3.value)


    def spawn_normal_particle(self, button):
        self.particle = gb.BallParticle(self.canvas, (255,90,180), .05, False, self.canon_origin, (random.uniform(-0.4, -0.1), 0.0), 1 / self.clock.fps*3, g=-9.8)

    def spawn_collidable_particle(self, button):
        print('')
        # self.particle = gb.BallCollidableParticle(self.canvas, (255,90,180), .05, False, self.canon_origin, (random.uniform(-0.4, -0.1), 0.0), 1 / self.clock.fps*3, g=-9.8)
        self.particle = gb.BallCollidableParticle(self.canvas, (255,90,180), .05, False, self.canon_origin, self.canon_dir, 1 / self.clock.fps*3, g=-9.8)

    def color_reset(self, button):
        print('color reset')
        for slider in (self.slider_r, self.slider_g, self.slider_b):
            slider.reset()

    def draw_main(self, canvas: gb.Canvas):
        canvas.fill(self.cols['bg'])



        points = gb.Points((0.0, 0.0), (0.6, 0.1), (0.4, 0.6))


        self.th0 = self.slider3.value
        self.dth -= .1 * self.slider.value
        self.th = self.dth + self.th0
        color = int(self.slider_r.value), int(self.slider_g.value), int(self.slider_b.value)
        canvas.draw_polygon(color, points.rotate(self.th, (0.4, 0.2)).scale(self.slider2.value))

        self.frame.update(self)
        self.frame_rgb.update(self)
        self.frame_bt.update(self)
        self.frame_bt2.update(self)
        self.frame_bt3.update(self)
        self.frame_bt4.update(self)

        # scope
        x = self.clock.t
        total_frame_time = 1 / self.real_fps if self.real_fps != 0 else 0
        y = (self.last_active_frame_time * self.clock.fps - 1, total_frame_time * self.clock.fps - 1)
        self.scope.append(x, y)
        self.scope.update(self)

        canvas.draw_line((255,0,0), self.canon_origin, self.canon_origin+self.canon_dir, 1)

        lines = [
            ((-.9, 0.1), (-0.2, 0.1)),
            ((-1.2, -0.4), (-0.9, 0.1)),
            ((-1.5, 0.0), (-1.3, -0.3)),
            ((-1.5, 0.0), (-1.5, .4)),
            ((-1.5, -0.6), (-1.0, -0.6)),
            ((-1.5, -0.6), (-1.5, -0.3)),
            ((-1.0, -0.4), (-1.0, -0.6)),
            ]


        x,y = self.mouse.pos
        line1 = Vector2(.3,0.0).rotate(self.th*180/math.pi)+ (1.1, 0.4), (1.1, 0.4)
        xx, yy = (1.1, 0.4)
        line2 = (xx, yy), (xx+.4, yy+.2)

        for line in lines:
            self.canvas.draw_line((255, 255, 0), line[0], line[1], 4)

        if self.particle is not None:
            if isinstance(self.particle, gb.BallCollidableParticle):
                self.particle.interference_lines = lines
                self.particle.step()
            else:
                self.particle.step()
            self.particle.draw()



        inter = gb.find_lines_intersection(line1[0], line1[1], line2[0], line2[1], True, ret_reflection=True)

        color = (255,0,0) if gb.find_lines_intersection(line1[0], line1[1], line2[0], line2[1], False) is not None else (255, 255, 0)

        self.canvas.draw_line(color, line1[0], line1[1], 4)
        self.canvas.draw_line(color, line2[0], line2[1], 4)
        if inter is not None:
            self.canvas.draw_line((255,255,0), inter[0], inter[0]+inter[1])







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


