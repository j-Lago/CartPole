import pygame
import sys
from datetime import datetime


class Screen:
    def __init__(self, window_size: tuple[int, int] = (1600, 900), canvas_size: tuple[int, int] = (1920, 1080), fps:float=60.0, antialiasing:bool=True, fullscreen=False):
        self.fullscreen = fullscreen
        self.antialiasing = antialiasing
        self.window_size = window_size
        self.fps = fps
        self.ticks = 0
        self.extra_info = []

        self.active_canvas = 'main'
        self.show_info = False
        self.info_position = (30, 30)

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

        self.tabs = {
            'main' : {'canvas': pygame.surface.Surface(canvas_size, pygame.SRCALPHA), 'bg_color': (30, 45, 30), 'draw': self.draw_main, 'shortcut': pygame.K_F1},
            'menu' : {'canvas': pygame.surface.Surface(canvas_size, pygame.SRCALPHA), 'bg_color': (45, 30, 30), 'draw': self.draw_menu, 'shortcut': pygame.K_F2},
            'extra': {'canvas': pygame.surface.Surface(canvas_size, pygame.SRCALPHA), 'bg_color': (30, 45, 45), 'draw': self.draw_extra, 'shortcut': pygame.K_F3},
        }

        self.clock = pygame.time.Clock()
        self.loop()

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
                    if event.key == pygame.K_F12:
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
                        if event.key == self.tabs[tab_key]['shortcut']:
                            self.active_canvas = tab_key

            canvas = self.tabs[self.active_canvas]['canvas']
            canvas.fill(self.tabs[self.active_canvas]['bg_color'])
            self.tabs[self.active_canvas]['draw'](canvas)

            self.window.fill(self.cols['screen_bg'])
            blit_with_aspect_ratio(self.window, self.tabs[self.active_canvas]['canvas'], self.antialiasing)

            if self.show_info:
                info_list = [f'fps: {self.clock.get_fps():.1f} Hz',
                             f'sim_time: {self.ticks / self.fps:.1f} s',
                             f'canvas_res: {canvas.get_size()} px',
                             f'window_res: {self.window.get_size()} px',
                             f'mouse: {pygame.mouse.get_pos()} px',
                             *self.extra_info
                             ]

                info_pos = self.info_position
                draw_text_list(self.window, info_list, self.fonts['info'], self.cols['info'], info_pos, 26)

            pygame.display.flip()
            self.clock.tick(self.fps)
            self.ticks += 1



    def draw_main(self, canvas):
        pygame.draw.circle(canvas, (30, 255, 30, 128), (200, 200), 200)
        pygame.draw.circle(canvas, (30, 30, 255), (350, 250), 200)
        render_and_blit_message(canvas, datetime.now().strftime("%H:%M:%S"), self.fonts['default'], (30, 120, 30, 128))
        width = 2
        pygame.draw.line(canvas, (255, 255, 255), (200, 200), (600, 500), width=width)
        pygame.draw.line(canvas, (255, 255, 255), (600, 500), (1000, 500), width=width)
        pygame.draw.line(canvas, (255, 255, 255), (1000, 500), (1000, 800), width=width)

    def draw_menu(self, canvas):
        prtsc = self.tabs['main']['canvas'].copy()
        prtsc.set_alpha(128)
        blit_with_aspect_ratio(canvas, prtsc)

        text_surface=render_message('MENU', self.fonts['default'], (0, 0, 0))
        text_rect = text_surface.get_rect(center=(canvas.get_width() // 2, canvas.get_height() // 2))
        pygame.draw.rect(canvas, (255, 255, 30, 128), text_rect, border_radius=30)
        canvas.blit(text_surface, text_rect)

    def draw_extra(self, canvas):
        render_and_blit_message(canvas, 'EXTRA', self.fonts['default'], (240, 120, 30, 128))




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

def render_and_blit_message(canvas, text, font, color):
    text_surface = render_message(text, font, color)
    text_rect = text_surface.get_rect(center=(canvas.get_width() // 2, canvas.get_height() // 2))
    canvas.blit(text_surface, text_rect)


def draw_text_list(canvas, info_list, font, color, pos, vspace):
    for l, info in enumerate(info_list):
        info_render = font.render(info, True, color)
        canvas.blit(info_render, (pos[0], pos[1] + vspace * l))


if __name__ == '__main__':
    Screen()