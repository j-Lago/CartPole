import pygame
from datetime import datetime
from canvas import Canvas
from inputs import Joystick, JOYBUTTON
import math
from canvas import rotate_vec2s
from random import random, randint, uniform, choice
from particles import BallParticle, Particles, TextParticle
from pygame import Vector2
from lerp import lerp, lerp_vec2, lerp_vec3
from screen import Screen, render_and_blit_message, blit_with_aspect_ratio, render_message


class Game(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tabs = {
            'test': Canvas(self.canvas_size, pygame.SRCALPHA, bg_color=(30, 45, 30), draw_fun = self.draw_main, shortcut=pygame.K_F2),
            'rocket': Canvas(self.canvas_size, pygame.SRCALPHA, bg_color= (15, 15, 15), draw_fun=self.draw_rocket, shortcut=pygame.K_F1),
            'menu': Canvas(self.canvas_size, pygame.SRCALPHA, bg_color=(15, 15, 15), draw_fun=self.draw_menu, shortcut=pygame.K_F3)
        }
        self.active_tab = 'rocket'
        self.last_active_tab = self.active_tab
        self.event_loop_callback = self.process_user_input_event

        self.steer = None
        self.throttle = None
        self.throttle_min = 0.05
        for i in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            self.steer = Joystick(joystick, 2)
            self.throttle = Joystick(joystick, 1)

        self.particles = Particles(20000)
        self.text_particles = Particles(500)
        self.particles_fonts = [
            pygame.font.SysFont('Times', 28),
            pygame.font.SysFont('Times', 34),
            pygame.font.SysFont('Times', 40),
        ]
        self.letters = [chr(i) for i in range(945, 970) if i != 962]  #choice(('0', '1')), #choice(tuple(chr(i) for i in range(97, 123))),

        self.loop()

    def process_user_input_event(self, event):

        keys = pygame.key.get_pressed()
        if event.type == pygame.MOUSEBUTTONDOWN and keys[pygame.K_LCTRL]:
            if event.button == 5:
                self.tabs[self.active_tab].scale /= 1.1
            if event.button == 4:
                self.tabs[self.active_tab].scale *= 1.1

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.mouse_left.press(event.pos)
            if event.button == 2:
                self.mouse_middle.press(event.pos)
            if event.button == 3:
                self.mouse_right.press(event.pos)

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.mouse_left.release(event.pos)
            if event.button == 2:
                self.mouse_middle.release(event.pos)
            if event.button == 3:
                self.mouse_right.release(event.pos)

        if event.type == pygame.MOUSEMOTION:
            if self.mouse_left.pressed:
                self.mouse_left.drag(event.pos)
            if self.mouse_middle.pressed:
                self.mouse_middle.drag(event.pos)
            if self.mouse_right.pressed:
                self.mouse_right.drag(event.pos)

        if self.mouse_right.dragging:
            self.tabs[self.active_tab].bias = [int(self.mouse_right.drag_delta[0] + self.tabs[self.active_tab].last_bias[0]), int(self.mouse_right.drag_delta[1] + self.tabs[self.active_tab].last_bias[1])]
        else:
            self.tabs[self.active_tab].last_bias = self.tabs[self.active_tab].bias

    def draw_main(self, canvas: Canvas):

        center = canvas.bias
        scale = canvas.scale

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
        # blit_with_aspect_ratio(canvas, prtsc, True)

        # text_surface = render_message('MENU', self.fonts['default'], (0, 0, 0))
        # text_rect = text_surface.get_rect(center=(canvas.get_width() // 2, canvas.get_height() // 2))
        #
        # pygame.draw.rect(canvas, (120, 120, 30, 200), text_rect, border_radius=30)
        # canvas.blit(text_surface, text_rect)

    def draw_rocket(self, canvas):
        if self.steer is not None:
            self.steer.update()
            self.throttle.update()
            angle = self.steer.value * math.pi / 6
            throttle = max(self.throttle_min, -self.throttle.value)
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

        c, s = math.cos(angle), math.sin(angle)

        for _ in range(randint(round(20 * throttle), round(40 * throttle))):
            vel = Vector2(uniform(-0.07, .07), uniform(-1.9, -3.8))
            self.particles.append(BallParticle(canvas,
                                               lerp_vec3(lerp_vec3((255, 60, 0), (200, 200, 60), random()),(255, 255, 255), random() * 0.5),
                                               uniform(.003, .006),
                                               pos=lerp_vec2(emmit_l, emmit_r, random()),
                                               vel=vel.rotate_rad(angle),
                                               dt=1 / self.fps, lifetime=uniform(.2, .6), g=0))

        self.particles.step_and_draw()



if __name__ == '__main__':
    Game()