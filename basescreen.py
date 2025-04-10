import time

import pygame
import sys
from canvas import Canvas
from mouse import Mouse
from utils import remap
from filters import MediaMovel
from popup import PopUp, PopUpText
from pygame import Vector2
from lerp import lerp_vec3

class BaseScreen:
    def __init__(self, window_size: tuple[int, int] = (1600, 900),
                 canvas_size: tuple[int, int] = (1920, 1080),
                 fps: float = 60.0,
                 antialiasing: bool = True,
                 fullscreen: bool = False,
                 flags: int = pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF
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

        pygame.init()



        self._flags = flags
        self.fullscreen = fullscreen
        self.antialiasing = antialiasing
        self.window_size = window_size
        self.canvas_size = canvas_size
        self.fps = fps

        self.mm_fps = MediaMovel(20)
        self.mm_frame_time = MediaMovel(20)

        self.ticks = 0
        self.extra_info = []
        self.event_loop_callback = None
        self.active_tab = None
        self.last_active_tab = None
        self.info_position = (30, 30)
        self.last_active_frame_time = 0.0
        self.real_fps = 0.0
        self.last_time = time.perf_counter()

        self.mouse = Mouse()



        if self.fullscreen:
            self.window = Canvas(surface=pygame.display.set_mode((0, 0), pygame.FULLSCREEN))
        else:
            self.window = Canvas(surface=pygame.display.set_mode(window_size, self._flags))


        self.cols = {
            'screen_bg': (30, 30, 30),
            'info': (220, 200, 90),
        }

        self.fonts = {
            'info': pygame.font.SysFont('Consolas', 22),
            'small': pygame.font.SysFont('Courier New', 28),
            'default': pygame.font.SysFont('Courier New', 72),
        }

        self.info_popup = PopUpText(self.window, alpha=180, pos=(10, -10), size=(400, 250), flags=flags,
                                    color=(255, 128, 128), text='', font=self.fonts['info'], visible=True, border_radius=13, border_width=2)

        self.tabs = dict()
        self.clock = pygame.time.Clock()

    @property
    def t(self):
        return self.ticks / self.fps

    @property
    def mouse_pos(self):
        return self.mouse.pos

    @property
    def mouse_world_pos(self):
        canvas = self.tabs[self.active_tab]
        return canvas.screen_to_world_v2(remap(self.mouse.pos, self.window, canvas))

    def loop(self):
        while True:
            for event in pygame.event.get():
                keys = pygame.key.get_pressed()
                self.mouse.process_event(event, keys)

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    screen = pygame.display.set_mode(event.size, self._flags)
                    self.window_size = screen.get_size()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F10:
                        self.antialiasing = not self.antialiasing
                    elif event.key == pygame.K_F12:
                        self.info_popup.visible = not self.info_popup.visible
                    elif event.key == pygame.K_F11:
                        self.fullscreen = not self.fullscreen
                        if self.fullscreen:
                            pygame.display.quit()
                            pygame.display.init()
                            self.window = Canvas(surface=pygame.display.set_mode((0, 0), pygame.FULLSCREEN))
                        else:
                            self.window = Canvas(surface=pygame.display.set_mode(self.window_size, self._flags))
                    elif event.key == pygame.K_a:
                        self.antialiasing = not self.antialiasing

                    for tab_key in self.tabs:
                        if event.key == self.tabs[tab_key].shortcut:
                            if self.active_tab != tab_key:
                                self.last_active_tab = self.active_tab
                                self.active_tab = tab_key
                                self.tabs[tab_key].got_focus()

                if self.event_loop_callback is not None:
                    self.event_loop_callback(event)


            # draw
            self.window.fill(self.cols['screen_bg'])

            canvas = self.tabs[self.active_tab]
            canvas.fill(self.tabs[self.active_tab]._bg_color)
            canvas.draw()

            blit_with_aspect_ratio(self.window, self.tabs[self.active_tab], self.antialiasing)

            self.info_popup.main_canvas = self.window
            self.info_popup.draw()
            self.info_popup.blit_to_main()

            self.mm_fps.append(self.real_fps)
            self.mm_frame_time.append(self.last_active_frame_time)

            self.info_popup.text = [
                f'fps: {self.mm_fps.value:.1f} Hz',
                f'frame_time: {self.mm_frame_time.value * 1000:.1f} ms ({self.mm_frame_time.value * self.fps * 100.0:.1f}%)',
                f'sim_time: {self.ticks / self.fps:.1f} s',
                f'antialiasing: {self.antialiasing}',
                f'active_tab: {self.active_tab} ({self.tabs[self.active_tab].ticks / self.fps:.1f} s)',
                f'canvas_res: {canvas.get_size()} px',
                f'window_res: {self.window.get_size()} px',
                f'mouse: {pygame.mouse.get_pos()} px',
                f'mouse_world: ({self.mouse_world_pos[0]:.2f}, {self.mouse_world_pos[1]:.2f})',
                f'global_relative_scale: {self.tabs[self.active_tab].relative_scale}',
                f'global_scale: {self.tabs[self.active_tab].scale}',
                f'global_bias: {self.tabs[self.active_tab].bias}',
                *self.extra_info
                ]

                # info_pos = self.info_position
                # draw_text_list(self.window.surface, info_list, self.fonts['info'], self.cols['info'], info_pos, 26)

            pygame.display.flip()
            self.ticks += 1
            self.tabs[self.active_tab].ticks += 1

            t = time.perf_counter()
            self.last_active_frame_time = (t - self.last_time)

            self.real_fps = self.clock.get_fps()
            self.clock.tick(self.fps)
            self.last_time = time.perf_counter()




        for n, info in enumerate(infos):
            canvas.blit(renders[n], canvas.screen_to_world_rect(rects[n]))
            print(y_max)











def blit_with_aspect_ratio(dest: Canvas, source: Canvas, antialiasing=True, offset: tuple[int, int] | None = None):
    source_size = source.get_size()
    dest_size = dest.get_size()

    source_ratio = source_size[0] / source_size[1]
    dest_ratio = dest_size[0] / dest_size[1]

    if source_size == dest_size:
        scaled_surface = source.copy()
        if offset is None:
            offset = (0, 0)
    else:
        rescale = pygame.transform.smoothscale if antialiasing else pygame.transform.scale
        if source_ratio > dest_ratio:
            new_width = dest_size[0]
            new_height = int(dest_size[0] / source_ratio)
        else:
            new_height = dest_size[1]
            new_width = int(dest_size[1] * source_ratio)
        scaled_surface = rescale(source.surface, (new_width, new_height))
        if offset is None:
            offset = (dest_size[0] - new_width) // 2, (dest_size[1] - new_height) // 2   # centralizada
    dest.blit(scaled_surface, dest.screen_to_world_v2(offset))



def render_message(text, font, color):
    text_surface = font.render(text, True, color[:3])
    if len(color) == 4:
        text_surface.set_alpha(color[3])
    return text_surface


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


