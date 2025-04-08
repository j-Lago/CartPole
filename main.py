import pygame
from datetime import datetime
from canvas import Canvas
from inputs import Joystick, JOYBUTTON
import math
from canvas import rotate_vec2s, resolution_map
from random import random, randint, uniform, choice
from particles import BallParticle, Particles, TextParticle
from pygame import Vector2
from lerp import lerp, lerp_vec2, lerp_vec3
from basescreen import BaseScreen, render_and_blit_message
from mouse import MouseButton, MouseScroll, Mouse
from popup import PopUp
import numpy as np
from _collections import deque

class Example(BaseScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.mouse.left.press_callback = self.left_click
        self.mouse.right.press_callback = self.right_click
        self.mouse.scroll.up_callback = self.scroll_up
        self.mouse.scroll.down_callback = self.scroll_down

        self.tabs = {
            'rocket': Canvas(self.canvas_size, pygame.SRCALPHA, bg_color=(15, 15, 15), draw_fun=self.draw_rocket, shortcut=pygame.K_F1),
            'test'  : Canvas(self.canvas_size, pygame.SRCALPHA, bg_color=(30, 45, 30), draw_fun =self.draw_main, shortcut=pygame.K_F2),
            'menu'  : Canvas(self.canvas_size, pygame.SRCALPHA, bg_color=(15, 15, 15), draw_fun=self.draw_menu, shortcut=pygame.K_F3)
        }
        self.active_tab = 'rocket'
        self.last_active_tab = self.active_tab
        self.event_loop_callback = self.process_user_input_event

        self.popup = PopUp(self.tabs['rocket'], alpha=200, pos=(0.-1.4, 0.1), size=(400, 250), flags=pygame.SRCALPHA, draw_fun=self.draw_popup)
        self.popup_plot = deque(maxlen=200)
        self.popup_rolling = True
        self.popup_freq = 4.0
        self.popup_amp = 0.7
        self.popup_t = 0.0


        self.steer = None
        self.throttle = None
        self.throttle_min = 0.05
        for i in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            self.steer = Joystick(joystick, 2)
            self.throttle = Joystick(joystick, 4, normalization=lambda x: x)

        self.particles = Particles(20000)
        self.text_particles = Particles(500)
        self.particles_fonts = [
            pygame.font.SysFont('Times', 28),
            pygame.font.SysFont('Times', 34),
            pygame.font.SysFont('Times', 40),
        ]
        self.letters = [chr(i) for i in range(945, 970) if i != 962]  #choice(('0', '1')), #choice(tuple(chr(i) for i in range(97, 123))),

        self.loop()

    def left_click(self, button: MouseButton):
        c = self.tabs[self.active_tab]
        pos = resolution_map(self.tabs[self.active_tab], self.window, button.press_pos)
        pos = self.tabs[self.active_tab].screen_to_world_v2(pos)
        print(f'{self.window.get_size()=} {c.get_size()} | {button.press_pos=}, {c.scale=}, {c.bias=} -> {pos=}')
        for _ in range(1000):
            vel = Vector2(uniform(-0.07, .07), uniform(-1.9, -3.8))
            self.particles.append(BallParticle(self.tabs['rocket'],
                                               lerp_vec3(lerp_vec3((0, 60, 255), (60, 200, 200), random()),(255, 255, 255), random() * 0.5),
                                               uniform(.003, .006),
                                               pos=pos,
                                               vel=vel.rotate_rad(uniform(0.0, 2*math.pi)),
                                               dt=1 / self.fps, lifetime=uniform(.2, .6), g=0))

    def right_click(self, button: MouseButton):
        pass

    def scroll_up(self, scroll: MouseScroll):
        if scroll.up_keys[pygame.K_LCTRL]:
            self.tabs[self.active_tab].scale /= 1.1

    def scroll_down(self, scroll: MouseScroll):
        if scroll.down_keys[pygame.K_LCTRL]:
            self.tabs[self.active_tab].scale *= 1.1

    def process_user_input_event(self, event):
        if self.mouse.right.dragging:
            self.tabs[self.active_tab].bias = [int(self.mouse.right.drag_delta[0] + self.tabs[self.active_tab].last_bias[0]), int(self.mouse.right.drag_delta[1] + self.tabs[self.active_tab].last_bias[1])]
        else:
            self.tabs[self.active_tab].last_bias = self.tabs[self.active_tab].bias

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.popup.pos = (self.popup.pos[0]-.05, self.popup.pos[1])
            elif event.key == pygame.K_RIGHT:
                self.popup.pos = (self.popup.pos[0]+.05, self.popup.pos[1])
            elif event.key == pygame.K_UP:
                self.popup.pos = (self.popup.pos[0], self.popup.pos[1]+.05)
            elif event.key == pygame.K_DOWN:
                self.popup.pos = (self.popup.pos[0], self.popup.pos[1]-.05)
            elif event.key == pygame.K_r:
                self.popup_plot.clear()
                self.popup_rolling = not self.popup_rolling
            elif event.key == pygame.K_v:
                self.popup.visible = not self.popup.visible

    def draw_main(self, canvas: Canvas):
        center = canvas.bias
        width = 1
        M = 10
        grid_color = (100, 100, 100)
        for m in range(4 * M + 1):
            canvas.draw_line(grid_color, (-2 + m / M, -1), (-2 + m / M, 1), width=width)
        for m in range(2 * M + 1):
            canvas.draw_line(grid_color, (-2, -1 + m / M), (2, -1 + m / M), width=width)

        radius = 0.1
        for n in range(11):
            canvas.draw_circle((180, 255, 180), (+0, +0), radius * n, width=1)
        canvas.draw_circle((255, 0, 0), (-1, -1), radius)
        canvas.draw_circle((0, 255, 0), (-1, +1), radius)
        canvas.draw_circle((0, 0, 255), (+1, +1), radius)
        canvas.draw_circle((255, 255, 0), (+1, -1), radius)

        render_and_blit_message(canvas, datetime.now().strftime("%H:%M:%S"), self.fonts['default'],
                                (240, 240, 180, 128), relative_scale=self.tabs[self.active_tab].relative_scale, center=center)

    def draw_menu(self, canvas):
        prtsc = self.tabs[self.last_active_tab].copy()
        prtsc.set_alpha(128)
        offset = (-canvas.get_world_rect()[2] / 2, canvas.get_world_rect()[3] / 2)
        canvas.blit(prtsc, offset)


    def draw_popup(self, canvas):

        rect = canvas.get_world_rect()
        xmin, xmax = rect[0], rect[0] + rect[2]
        ymin, ymax = rect[1] - rect[3], rect[1]
        w = rect[2]
        N = self.popup_plot.maxlen
        xscale = (xmax - xmin) / N / self.fps
        xbias = xmin

        color=(0, 255, 255)
        color_line = color
        color_grid = lerp_vec3(color, (30, 30, 30), 0.7)
        color_bf = lerp_vec3(color, (30, 30, 30), 0.9)
        width=2

        canvas.draw_rect(color_bf, rect, 0, 15)

        canvas.draw_line(color_grid, (xmin, 0), (xmax, 0), 1)
        canvas.draw_line(color_grid, (0, ymin), (0, ymax), 1)


        self.popup_freq += uniform(-0.02, 0.02)
        self.popup_amp += uniform(-0.01, 0.01)
        self.popup_t += self.fps

        n = (self.ticks % N)
        if n == 0 and not self.popup_rolling:
            self.popup_plot.clear()
        x = self.popup_t * xscale
        y = self.popup_amp*math.sin(x*self.popup_freq) + uniform(-.1, 0.1)


        if not self.popup_rolling:
            seq = [(xx % w + xmin, yy) for xx, yy in self.popup_plot]
        else:
            seq = [( ( (xx + (w-x)) % w + xmin) , yy) for xx, yy in self.popup_plot]
            seq = sorted(seq, key=lambda pair: pair[0])
        self.popup_plot.append((x, y))



        if len(seq)> 2:
            canvas.draw_lines(color_line, False, seq, width)

        canvas.draw_rect(color, rect, width, 15)


    def draw_rocket(self, canvas):
        if self.steer is not None:
            self.steer.update()
            self.throttle.update()
            angle = self.steer.value * math.pi / 6
            throttle = max(self.throttle_min, self.throttle.value)
        else:
            angle = 0.0
            throttle = self.throttle_min

        if self.ticks % 2 == 0:
            for _ in range(11):
                self.text_particles.append(
                    TextParticle(canvas,
                                 color=lerp_vec3((90, 250, 90), (30, 90, 30), random()),
                                 text=choice(self.letters),
                                 font=choice(self.particles_fonts),
                                 pos=(uniform(-1.8, 1.8), 1.1),
                                 vel=(0, -0.8), dt=1/self.fps, g=-98, lifetime=2,
                                 ))
        self.text_particles.step_and_draw()


        canvas.draw_polygon((90, 90, 100), rotate_vec2s(((0.06, 0.05), (0.08, -0.1), (-0.08, -0.1), (-0.06, 0.05)), angle))  # angle
        canvas.draw_polygon((120, 120, 130),
                            ((0.1, 0.0), (0.1, 0.6), (0.06, 0.75), (0.0, 0.8), (-0.06, 0.75), (-0.1, 0.6), (-0.1, 0.0)))

        canvas.draw_circle((255, 200, 60), (0, 0.25), 0.05, width=0, draw_top_left=True, draw_bottom_right=True)
        canvas.draw_circle((0, 0, 0), (0, 0.25), 0.05, width=0, draw_top_right=True, draw_bottom_left=True)

        emmit_l = Vector2(-0.08, -0.082).rotate_rad(angle)
        emmit_r = Vector2(0.08, -0.082).rotate_rad(angle)

        # c, s = math.cos(angle), math.sin(angle)

        for _ in range(randint(round(20 * throttle), round(40 * throttle))):
            vel = Vector2(uniform(-0.07, .07), uniform(-1.9, -3.8))
            self.particles.append(BallParticle(canvas,
                                               lerp_vec3(lerp_vec3((255, 60, 0), (200, 200, 60), random()),(255, 255, 255), random() * 0.5),
                                               uniform(.003, .006),
                                               pos=lerp_vec2(emmit_l, emmit_r, random()),
                                               vel=vel.rotate_rad(angle),
                                               dt=1 / self.fps, lifetime=uniform(.2, .6), g=0))
        self.particles.step_and_draw()

        self.popup.draw()
        self.popup.blit_to_main()



if __name__ == '__main__':
    Example()