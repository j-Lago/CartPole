import pygame
import sys
from datetime import datetime
from canvas import Canvas
from inputs import Joystick, JOYBUTTON
import math
from canvas import rotate_vec2s
from random import random, randint, uniform, choice
from particles import BallParticle, Particles, TextParticle
from pygame import Vector2
from lerp import lerp, lerp_vec2, lerp_vec3

class MouseButton:
    def __init__(self):
        self.press_time = None
        self.release_time = None
        self.press_pos = None
        self.release_pos = None
        self.drag_pos = None
        self.pressed = False
        self.dragging = False

    def press(self, pos):
        self.press_time = pygame.time.get_ticks()
        self.press_pos = pos
        self.pressed = True

    def release(self, pos):
        self.release_time = pygame.time.get_ticks()
        self.release_pos = pos
        self.pressed = False
        self.drag_pos = pos
        self.dragging = False

    def drag(self, pos):
        self.drag_pos = pos
        self.dragging = True

    @property
    def drag_delta(self):
        return self.drag_pos[0]-self.press_pos[0], self.drag_pos[1]-self.press_pos[1]


class Screen:
    def __init__(self, window_size: tuple[int, int] = (1600, 900),
                 canvas_size: tuple[int, int] = (1920, 1080),
                 fps: float = 60.0,
                 antialiasing: bool = True,
                 fullscreen: bool = False,
                 ):
        """
        Inicializa uma janela pygame.
        Alguns atalhos de teclado são pre-configurados:
            F10 ativa/destiva antialiasing
            F11 alterna entre modo fullscreen e windoned
            F12 mostra informações da renderização da aplicação
            alt+F4 fecha a aplicação
            ctr+scroll zoom
            right mouse drag
            F1..F3 altera o canvas (tabs) que será renderizado (apenas exemplo, todo: retirar depois)

        :param window_size: tamanho inicial da janela para o modo windoned
        :param canvas_size: tamanho da superficie de renderização. Essa superficie ao final de cada frame será redimensionada para o tamanho atual da janela
        :param fps: taxa de quadros por segundo
        :param antialiasing: define se será ou não aplicado antialiasing no redimensionamento da janela. Não tem efeito se window_size == canvas_size
        :param fullscreen: inicia no modo fullscreen
        """
        self.fullscreen = fullscreen
        self.antialiasing = antialiasing
        self.window_size = window_size
        self.canvas_size = canvas_size
        self.fps = fps
        # self.tabs['main']['scale'] = 1.0
        # self.tabs['main']['bias'] = [0, 0]
        # self.tabs['main']['last_bias'] = [0, 0]
        self.ticks = 0
        self.extra_info = []

        self.event_loop_callback = None
        self.active_tab = 'main'
        self.show_info = False
        self.info_position = (30, 30)

        self.mouse_left = MouseButton()
        self.mouse_middle = MouseButton()
        self.mouse_right = MouseButton()

        pygame.init()

        if self.fullscreen:
            self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.window = pygame.display.set_mode(window_size, pygame.RESIZABLE)

        self.cols = {
            'screen_bg': (30, 30, 30),
            'info': (220, 200, 90),
        }

        self.fonts = {
            'info': pygame.font.SysFont('Consolas', 26),
            'default': pygame.font.SysFont('Courier New', 200),
        }

        self.tabs = dict()
        self.clock = pygame.time.Clock()

    def loop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                    self.window_size = screen.get_size()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F10:
                        self.antialiasing = not self.antialiasing
                    elif event.key == pygame.K_F12:
                        self.show_info = not self.show_info
                    elif event.key == pygame.K_F11:
                        self.fullscreen = not self.fullscreen
                        if self.fullscreen:
                            pygame.display.quit()
                            pygame.display.init()
                            self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        else:
                            self.window = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)
                    elif event.key == pygame.K_a:
                        self.antialiasing = not self.antialiasing

                    for tab_key in self.tabs:
                        if event.key == self.tabs[tab_key].shortcut:
                            self.active_tab = tab_key

                if self.event_loop_callback is not None:
                    self.event_loop_callback(event)

            canvas = self.tabs[self.active_tab]
            canvas.fill(self.tabs[self.active_tab].bg_color)
            self.tabs[self.active_tab].draw(canvas)

            self.window.fill(self.cols['screen_bg'])
            blit_with_aspect_ratio(self.window, self.tabs[self.active_tab], self.antialiasing)

            if self.show_info:
                info_list = [f'fps: {self.clock.get_fps():.1f} Hz',
                             f'sim_time: {self.ticks / self.fps:.1f} s',
                             f'antialiasing: {self.antialiasing}',
                             f'active_tab: {self.active_tab} ({self.tabs[self.active_tab].ticks / self.fps:.1f} s)',
                             f'canvas_res: {canvas.get_size()} px',
                             f'window_res: {self.window.get_size()} px',
                             f'mouse: {pygame.mouse.get_pos()} px',
                             f'global_scale: {self.tabs[self.active_tab].scale}',
                             f'global_bias: {self.tabs[self.active_tab].bias}',
                             *self.extra_info
                             ]

                info_pos = self.info_position
                draw_text_list(self.window, info_list, self.fonts['info'], self.cols['info'], info_pos, 26)

            pygame.display.flip()
            self.clock.tick(self.fps)
            self.ticks += 1
            self.tabs[self.active_tab].ticks += 1



class Game(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tabs = {
            'main': Canvas(self.canvas_size, pygame.SRCALPHA, bg_color=(30, 45, 30), draw_fun = self.draw_main, shortcut=pygame.K_F1),
            'menu': Canvas(self.canvas_size, pygame.SRCALPHA, bg_color=(45, 30, 30), draw_fun=self.draw_menu, shortcut=pygame.K_F2),
            'extra': Canvas(self.canvas_size, pygame.SRCALPHA, bg_color= (15, 15, 15), draw_fun=self.draw_extra, shortcut=pygame.K_F3)
        }
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
                                (240, 240, 180, 128), relative_scale=self.tabs['main'].relative_scale, center=center)

    def draw_menu(self, canvas):
        prtsc = self.tabs['main'].copy()
        prtsc.set_alpha(128)
        blit_with_aspect_ratio(canvas, prtsc)

        text_surface = render_message('MENU', self.fonts['default'], (0, 0, 0))
        text_rect = text_surface.get_rect(center=(canvas.get_width() // 2, canvas.get_height() // 2))
        pygame.draw.rect(canvas, (255, 255, 30, 128), text_rect, border_radius=30)
        canvas.blit(text_surface, text_rect)

    def draw_extra(self, canvas):
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




def blit_with_aspect_ratio(dest: pygame.surface.Surface, source: pygame.surface.Surface, antialiasing=True, offset: tuple[int, int] | None = None):


    source_width, source_height = source.get_size()
    dest_width, dest_height = dest.get_size()

    source_ratio = source_width / source_height
    dest_ratio = dest_width / dest_height

    if source.get_size() == dest.get_size():
        scaled_surface = source.copy()
        if offset is None:
            offset = (0, 0)
    else:
        rescale = pygame.transform.smoothscale if antialiasing else pygame.transform.scale
        if source_ratio > dest_ratio:
            new_width = dest_width
            new_height = int(dest_width / source_ratio)
        else:
            new_height = dest_height
            new_width = int(dest_height * source_ratio)
        scaled_surface = rescale(source, (new_width, new_height))
        if offset is None:
            offset = (dest_width - new_width) // 2, (dest_height - new_height) // 2   # centralizada
    dest.blit(scaled_surface, offset)



def render_message(text, font, color):
    text_surface = font.render(text, True, color[:3])
    if len(color) == 4:
        text_surface.set_alpha(color[3])
    return text_surface


def render_and_blit_message(canvas, text, font, color, relative_scale=1.0, **kwargs):
    if len(kwargs) == 0:
        kwargs['center'] = (canvas.get_width() // 2, canvas.get_height() // 2)
    text_surface = render_message(text, font, color)
    if relative_scale != 1:
        text_surface = pygame.transform.smoothscale_by(text_surface, relative_scale)

    text_rect = text_surface.get_rect(**kwargs)
    canvas.blit(text_surface, text_rect)


def draw_text_list(canvas, info_list, font, color, pos, vspace):
    for l, info in enumerate(info_list):
        info_render = font.render(info, True, color)
        canvas.blit(info_render, (pos[0], pos[1] + vspace * l))


def world_to_screen(vec2: tuple[float, float], scale: tuple[float, float] | float, bias: tuple[float, float]) -> tuple[int, int]:
    if isinstance(scale, float | int):
        scale = (scale, scale)
    screen_x = round(vec2[0] * scale[0] + bias[0])
    screen_y = round(-vec2[1] * scale[1] + bias[1])
    return screen_x, screen_y


if __name__ == '__main__':
    Game()